# GRC Application

<!-- sdcSDcaDSDvDSvasdvcaefcasecv -->

This is a Governance, Risk, and Compliance (GRC) application built with Django REST Framework backend and Vue.js frontend.

## Project Structure

```
GRC_SETUP/
├── backend/             # Django backend
│   ├── backend/         # Project settings
│   ├── grc/             # Main application
│   ├── manage.py        # Django management script
│   └── requirements.txt # Python dependencies
└── frontend/            # Vue.js frontend
    ├── public/          # Static files
    ├── src/             # Source code
    ├── package.json     # Node.js dependencies
    └── vue.config.js    # Vue configuration
```

## Backend Setup

### Prerequisites
- Python 3.8+
- pip

### Installation and Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

. Start the development server:
   ```bash
   python manage.py runserver
   ```

The backend API will be available at http://localhost:8000/

## Frontend Setup

### Prerequisites
- Node.js 14+
- npm or yarn

### Installation and Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install

   ```

3. Start the development server:
   ```bash
   npm run serve

   ```

The frontend application will be available at http://localhost:8080/

## Login Credentials

For testing purposes, use these hardcoded credentials:
- Email: admin@example.com
- Password: password123

## Git Workflow

### Creating a New Branch

1. Make sure you're on the main branch and it's up to date:
   ```bash
   git checkout main
   git pull origin main
   ```

2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
   Use a descriptive name that reflects what you're working on.

### Making Changes and Committing

1. Make your changes to the codebase.

2. Add the changes to staging:
   ```bash
   git add .  # Add all files
   # or
   git add path/to/specific/file  # Add specific files
   ```

3. Commit your changes with a descriptive message:
   ```bash
   git commit -m "Add login functionality"
   ```

### Pushing Changes to GitHub

1. Push your branch to the remote repository:
   ```bash
   git push origin feature/your-feature-name
   ```

2. If this is the first time pushing the branch, you can set upstream:
   ```bash
   git push -u origin feature/your-feature-name
   ```

### Creating a Pull Request

1. Go to the GitHub repository in your browser.
2. Switch to your branch.
3. Click "Compare & pull request".
4. Add a title and description of your changes.
5. Click "Create pull request".

### Merging Back to Main

After your pull request has been reviewed and approved:

1. Click "Merge pull request" on GitHub.
2. Delete the branch if it's no longer needed.

## Development Notes

- Backend API endpoints are prefixed with `/api/`
- Frontend uses Axios for API communication
- CORS is enabled for development
