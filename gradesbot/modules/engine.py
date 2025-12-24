import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
import os
from config import CHART_DIR
from modules.database import db

async def process_file(file_path, source_id):
    print(f"Processing file: {file_path}")
    
    # Load data
    if file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        # For PDF, we'd need a library like tabula-py or pdfplumber
        # Placeholder for PDF extraction logic
        print("PDF extraction not fully implemented in this snippet.")
        return

    # Assume columns: 'student_id', 'grade'
    # Clean data: remove withdrawals (grade 0)
    df_clean = df[df['grade'] > 0].copy()
    
    # Calculate stats
    mean = df_clean['grade'].mean()
    std = df_clean['grade'].std()
    median = df_clean['grade'].median()
    
    # Calculate Rank and Percentile
    df_clean['rank'] = df_clean['grade'].rank(ascending=False, method='min')
    df_clean['percentile'] = df_clean['grade'].rank(pct=True) * 100
    
    # Subject name from filename
    subject = os.path.basename(file_path).split('.')[0]
    
    # Process each student
    for _, row in df_clean.iterrows():
        student_id = str(row['student_id'])
        grade = row['grade']
        rank = int(row['rank'])
        percentile = round(row['percentile'], 2)
        
        # Generate Chart
        chart_path = generate_bell_curve(df_clean['grade'], grade, student_id, subject)
        
        # Save to DB
        db.add_grade(student_id, subject, grade, rank, percentile, str(source_id))
        
        # Notify student (to be implemented in notifier.py)
        from modules.notifier import notify_student
        await notify_student(student_id, subject, grade, rank, percentile, chart_path)

def generate_bell_curve(all_grades, student_grade, student_id, subject):
    plt.figure(figsize=(10, 6))
    sns.histplot(all_grades, kde=True, stat="density", color='skyblue', alpha=0.6)
    
    # Fit normal distribution
    mu, std = norm.fit(all_grades)
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    plt.plot(x, p, 'k', linewidth=2)
    
    # Mark student position
    plt.axvline(student_grade, color='red', linestyle='--', label=f'Your Grade: {student_grade}')
    plt.scatter([student_grade], [norm.pdf(student_grade, mu, std)], color='red', s=100, zorder=5)
    
    plt.title(f"Grade Distribution - {subject}")
    plt.xlabel("Grade")
    plt.ylabel("Density")
    plt.legend()
    
    chart_filename = f"{student_id}_{subject}_chart.png"
    chart_path = os.path.join(CHART_DIR, chart_filename)
    plt.savefig(chart_path)
    plt.close()
    return chart_path
