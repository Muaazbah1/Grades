import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
import os
import logging
from config import CHART_DIR
from modules.database import db

logger = logging.getLogger("DataEngine")

async def process_file(file_path, source_id):
    logger.info(f"Starting analysis for: {file_path}")
    
    try:
        # 1. Load data
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            # PDF support would require extra libraries like tabula-py
            logger.warning(f"PDF processing not yet implemented for {file_path}")
            return

        # Standardize column names (case-insensitive search)
        df.columns = [c.lower().strip() for c in df.columns]
        
        # Look for ID and Grade columns
        id_col = next((c for c in df.columns if 'id' in c or 'student' in c), None)
        grade_col = next((c for c in df.columns if 'grade' in c or 'mark' in c or 'result' in c), None)

        if not id_col or not grade_col:
            logger.error(f"Could not find ID or Grade columns in {file_path}. Columns: {df.columns}")
            return

        # 2. Clean data: remove withdrawals (grade 0)
        df[grade_col] = pd.to_numeric(df[grade_col], errors='coerce')
        df_clean = df[df[grade_col] > 0].dropna(subset=[grade_col, id_col]).copy()
        
        if df_clean.empty:
            logger.warning(f"No valid grades found in {file_path}")
            return

        # 3. Calculate class stats
        mean = df_clean[grade_col].mean()
        std = df_clean[grade_col].std()
        
        # Calculate Rank and Percentile
        df_clean['rank'] = df_clean[grade_col].rank(ascending=False, method='min')
        df_clean['percentile'] = df_clean[grade_col].rank(pct=True) * 100
        
        subject = os.path.basename(file_path).split('.')[0]
        
        # 4. Get all registered users from DB
        registered_users = db.get_all_users()
        if not registered_users:
            logger.info("No registered users in database. Skipping notifications.")
            return

        # 5. Search for matches
        for user in registered_users:
            student_id = str(user['student_id'])
            
            # Find student in the dataframe
            match = df_clean[df_clean[id_col].astype(str) == student_id]
            
            if not match.empty:
                row = match.iloc[0]
                grade = row[grade_col]
                rank = int(row['rank'])
                percentile = round(row['percentile'], 2)
                
                logger.info(f"Match found! Student {student_id} got {grade}")
                
                # Generate Chart
                chart_path = generate_bell_curve(df_clean[grade_col], grade, student_id, subject)
                
                # Save to DB
                db.add_grade(student_id, subject, grade, rank, percentile, str(source_id))
                
                # Notify student
                from modules.notifier import notify_student
                await notify_student(student_id, subject, grade, rank, percentile, chart_path)

    except Exception as e:
        logger.error(f"Error in data engine: {e}")

def generate_bell_curve(all_grades, student_grade, student_id, subject):
    try:
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
    except Exception as e:
        logger.error(f"Failed to generate chart: {e}")
        return None
