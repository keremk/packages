# Infinite Package Stream Service

This project is a Python FastAPI based service that utilizes Pydantic and typing to expose an HTTP2 streaming endpoint. It provides an infinite stream of JSON encoded package information, generating an infinite random list of packages with dimensions (width, height, length) and a unique package id for each package.

## Getting Started

To get this service up and running on your local machine, follow these instructions.

### Prerequisites

Ensure you have Python 3.6+ installed on your system. You can download it from [here](https://www.python.org/downloads/).

### Installation

1. Clone the repository to your local machine:
```
git clone <repository-url>
```

2. Navigate to the project directory:
```
cd <project-directory>
```

3. Install the required dependencies:
```
pip install -r requirements.txt
```

### Running the Service

To start the FastAPI service, run the following command:
```
uvicorn main:app --reload
```
This will start the server on `http://127.0.0.1:8000`. You can access the streaming endpoint at `http://127.0.0.1:8000/packages/stream`.

## Usage

The service exposes a single endpoint `/packages/stream` which streams an infinite list of package information. Each package includes a unique ID, width, height, and length.

You can consume this stream using any HTTP client that supports HTTP2 streaming. For example, using `curl`:
```
curl http://127.0.0.1:8000/packages/stream
```

## Development

This project is structured as follows:

- `requirements.txt`: Lists all the Python dependencies required for the project.
- `models.py`: Defines the Pydantic model for a package.
- `main.py`: Contains the FastAPI app and endpoint definitions.
- `.env`: A file for environment configuration settings.
- `README.md`: Provides an overview of the project and setup instructions.

Feel free to explore and modify the code to suit your needs.

## License

This project is open-sourced under the MIT License. See the LICENSE file for more details.

