# AI Sales Intelligence & CRM Platform

An AI-powered full-stack CRM platform designed to help sales teams manage leads, customers, deals and activities while using machine learning and sales intelligence to improve decision-making.

## 🚀 Overview

The platform combines traditional CRM functionality with AI-driven sales analytics.

Sales teams can:

- Manage leads, customers and deals
- Track sales activities and follow-ups
- Score leads based on business attributes
- Predict deal win probability using machine learning
- Calculate weighted pipeline value
- Monitor sales performance through dashboards
- Interact with an AI Sales Copilot
- Manage authenticated users with role-based access

## ✨ Key Features

### CRM Management
- Lead management
- Customer management
- Deal management
- Sales pipeline tracking
- Activity and follow-up management

### AI & Machine Learning

**Lead Scoring**

Leads are automatically scored using factors such as:

- Lead source
- Industry
- Estimated deal value

Leads are classified into High, Medium and Low priority.

**Deal Win Prediction**

A machine learning model predicts the probability of a deal being won based on deal characteristics.

The system also calculates:

`ML Weighted Value = Deal Value × ML Win Probability`

**Sales Intelligence**

The dashboard provides:

- Pipeline value
- Weighted pipeline value
- Average win probability
- Won revenue
- Lost revenue
- Lead priority distribution
- Activity completion status

### 🤖 AI Sales Copilot

The Copilot provides sales-focused insights such as:

- Which leads should I call today?
- Which customers are high priority?
- Why is my pipeline weak?
- Which deals require attention?

The Copilot analyzes CRM data and provides actionable recommendations.

## 🏗️ System Architecture

```text
React Frontend
      │
      │ REST API
      ▼
FastAPI Backend
      │
      ├── Authentication & JWT
      ├── CRM APIs
      ├── Lead Scoring
      ├── Sales Analytics
      ├── AI Copilot
      └── ML Deal Prediction
      │
      ▼
SQLite Database