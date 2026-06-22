# Good Stuff Catering — Enterprise Management System (CMS)

![Architecture](https://img.shields.io/badge/Architecture-Three--Tier-blue)
![Backend](https://img.shields.io/badge/Backend-Python%20%7C%20Django-darkgreen)
![Frontend](https://img.shields.io/badge/Mobile-Kotlin%20%7C%20Android-purple)
![Security](https://img.shields.io/badge/Security-RBAC-red)

A robust, three-tier Catering Management System engineered to automate operational workflows, secure customer data, and provide real-time business intelligence for Good Stuff Catering. Developed as a comprehensive software architecture capstone at Rosebank International.

## System Architecture & Core Features

This system is strictly decoupled, separating the client presentation layers from the secure data and logic application servers.

- **Secure Role-Based Access Control (RBAC):** Django-powered backend enforcing strict authentication for Customers, Floor Staff, and Management.
- **Business Intelligence Dashboard:** An executive web portal featuring live data aggregation for booking trends, revenue calculations, and buffer stock alerts.
- **Automated Scheduling Logic:** Algorithmic validation of staff rosters against event guest counts and availability to prevent resource conflicts.
- **Mobile-First Client Presentation:** A lightweight Android client built in Kotlin for rapid customer booking and real-time floor staff inventory logging.
- **AI-Ready Data Modeling:** Fully normalized relational database schemas designed to easily integrate with predictive analytics pipelines in the future (e.g., forecasting inventory burn rates).

## Technology Stack

- **Backend API & Web Portal:** Python 3, Django 5, SQLite (Local Development)
- **Mobile Application:** Kotlin, Android Studio, XML/Jetpack Compose
- **Version Control & Documentation:** Git, GitHub

## Local Development Setup (Backend)

To spin up the secure backend application server locally:

1. **Clone the repository and enter the directory:**
   ```bash
   git clone [https://github.com/GosegoMatlokwe/GoodStuff-CMS-Backend]
   cd GoodStuffCMS
   ```
