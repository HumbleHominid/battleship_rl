terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    prefix = "terraform/state"
    # bucket is supplied at init time:
    #   terraform init -backend-config="bucket=YOUR_BUCKET"
    # or locally via backend.conf (see backend.conf.example)
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
