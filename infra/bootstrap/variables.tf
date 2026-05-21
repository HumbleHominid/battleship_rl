variable "project_id" {
  type        = string
  description = "GCP project ID"
}

variable "region" {
  type        = string
  description = "GCP region for the state bucket"
  default     = "us-central1"
}

variable "tf_state_bucket" {
  type        = string
  description = "Name for the GCS bucket that will store Terraform state"
}
