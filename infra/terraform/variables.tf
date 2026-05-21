variable "project_id" {
  type        = string
  description = "GCP project ID"
}

variable "region" {
  type        = string
  description = "GCP region"
  default     = "us-central1"
}

variable "github_repo" {
  type        = string
  description = "GitHub repo in owner/name format; scopes WIF to this repo only"
  default     = "mfryer/battleship-rl"
}

variable "tf_state_bucket" {
  type        = string
  description = "GCS bucket name storing Terraform state (created by bootstrap)"
}

variable "image_tag" {
  type        = string
  description = "Docker image tag to deploy. CI sets this to the git SHA. Defaults to a public placeholder for the initial apply."
  default     = "placeholder"
}
