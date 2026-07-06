import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

print("🚀 Starting the Machine Learning Pipeline...")

# 1. Ensure folders exist
os.makedirs('data', exist_ok=True)
os.makedirs('models', exist_ok=True)

# 2. Create a Mock Dataset
# In a real project, this would be thousands of rows from Kaggle or your own surveys.
data = {
    'Degree': ['B.Tech CS', 'B.Tech CS', 'BCA', 'B.Sc Stats', 'BBA', 'B.Tech IT', 'B.Tech Mech', 'B.Com'],
    'Primary_Skill': ['Python', 'Java', 'HTML/CSS', 'Python', 'Marketing', 'SQL', 'AutoCAD', 'Accounting'],
    'Interest': ['AI', 'Backend', 'UI/UX', 'Data', 'Business', 'Databases', 'Design', 'Finance'],
    'Recommended_Career': ['Data Scientist', 'Software Engineer', 'Frontend Developer', 'Data Analyst', 
                           'Digital Marketer', 'Database Admin', 'Mechanical Engineer', 'Financial Analyst']
}

df = pd.DataFrame(data)

# Save the raw data for our records
df.to_csv('data/career_dataset.csv', index=False)
print("✅ Mock dataset saved to data/career_dataset.csv")

# 3. Preprocess the Data (Machine Learning models only understand numbers)
# We will use LabelEncoders to convert text like "Python" into numbers like "1"
encoders = {}
for column in ['Degree', 'Primary_Skill', 'Interest']:
    encoders[column] = LabelEncoder()
    df[column] = encoders[column].fit_transform(df[column])

# Separate the inputs (X) from the output we want to predict (y)
X = df[['Degree', 'Primary_Skill', 'Interest']]
y = df['Recommended_Career']

# 4. Train the Model
model = RandomForestClassifier(random_state=42)
model.fit(X, y)
print("✅ Random Forest Model trained successfully!")

# 5. Save the Model and Encoders
joblib.dump(model, 'models/career_model.pkl')
joblib.dump(encoders, 'models/encoders.pkl')
print("✅ Model and Encoders saved to the models/ folder.")
print("🎉 Phase 2 Brain is ready to use!")