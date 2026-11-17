import os


os.environ["JWT_SECRET_KEY"] = "intentra-test-only-secret-key-that-must-never-be-used-in-production"
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ["MONGODB_DB_NAME"] = "intentra_test"
