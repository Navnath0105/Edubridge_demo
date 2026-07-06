# Edubridge:AI-Powered Career Counselor

## Overview
EduBridge is a comprehensive educational intelligence platform developed to address the gap between academic preparation and industry demands. By utilizing machine learning algorithms and generative AI, the platform provides personalized career guidance, identifies individual skill deficiencies, and offers a conversational interface to mentor students through their career transition phase.

## Problem Statement
Many students struggle to align their academic degrees with rapidly evolving industry trends. Lack of personalized guidance often leads to poor career decisions and an inability to bridge the "skill gap"—the difference between a student’s current technical expertise and the requirements of their desired profession.

## Proposed Solution & Methodology
EduBridge implements a multi-tiered architecture to solve this:

Recommendation Engine: Uses historical data and academic attributes (Degree, Skill, Interest) to perform predictive analysis, mapping student profiles to high-probability career outcomes.

Skill Gap Analysis Module: A comparative utility that maps user-provided skills against a curated set of industry-standard requirements, providing a direct link to the necessary learning resources.

Conversational AI Mentor: An integrated chatbot powered by the Google Gemini API, providing 24/7 personalized mentorship and clarification on career-related queries.

Admin Dashboard: A robust management interface for data analytics, allowing administrators to monitor platform usage trends and update the resource database.

## System Architecture
The system operates through three primary layers:

Data Tier: Pre-processed CSV-based datasets containing career mapping information.

Logic Tier: A Scikit-Learn model optimized for classification tasks and an API-based interaction layer for the generative AI agent.

Interface Tier: A Streamlit-based frontend, optimized for a modern, responsive user experience, featuring dynamic theme switching and modular navigation.

## Expected Outcomes
Personalized Roadmap: Students receive tailored advice that reflects their specific academic background.

Data-Driven Decisions: The platform reduces subjective error in career selection by relying on trained classification models.

Educational Efficiency: By identifying exactly which skills a student lacks, the platform minimizes wasted study time and increases the likelihood of professional placement.
