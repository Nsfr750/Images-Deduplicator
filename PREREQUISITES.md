# Prerequisites

Before you can run or contribute to the Images-Deduplicator project, you'll need to set up your development environment with the following prerequisites:

## System Requirements

- Python 3.8 or higher
- pip (Python package installer)
- Git (for version control)

## Python Dependencies

Install the required Python packages using the following command:

```bash
pip install -r requirements.txt
```

### Development Dependencies (Optional)

For development and testing, you might also need:

```bash
pip install -r requirements-dev.txt  # If available
```

## Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Nsfr750/Images-Deduplicator.git
   cd Images-Deduplicator
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

To start the application, run:

```bash
python main.py
```

## Building Documentation

If you want to build the documentation locally:

1. Install documentation dependencies:
   ```bash
   pip install -r docs/requirements.txt
   ```

2. Build the documentation:
   ```bash
   cd docs
   make html
   ```

## Testing

To run the test suite:

```bash
pytest
```

## Troubleshooting

If you encounter any issues:

1. Make sure all dependencies are properly installed
2. Check that you're using the correct Python version
3. Verify that your virtual environment is activated (if using one)
4. Check the [Issues](https://github.com/Nsfr750/Images-Deduplicator/issues) page for known problems

## Support

For additional help, please contact:
- Discord: [Join our server](https://discord.gg/BvvkUEP9)
- Email: nsfr750@yandex.com
