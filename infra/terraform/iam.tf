# --- Service accounts ---

resource "google_service_account" "cloud_run" {
  account_id   = "battleship-run"
  display_name = "Battleship RL Cloud Run"
}

resource "google_service_account" "ci" {
  account_id   = "battleship-ci"
  display_name = "Battleship RL CI/CD"
}

# --- CI/CD IAM bindings ---

# Push images to Artifact Registry (repo-scoped, not project-wide)
resource "google_artifact_registry_repository_iam_member" "ci_ar_writer" {
  repository = google_artifact_registry_repository.app.name
  location   = var.region
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.ci.email}"
}

# Update Cloud Run revisions
resource "google_project_iam_member" "ci_run_developer" {
  project = var.project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.ci.email}"
}

# Act as the Cloud Run service account when deploying
resource "google_service_account_iam_member" "ci_cloudrun_sa_user" {
  service_account_id = google_service_account.cloud_run.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.ci.email}"
}

# Read/write Terraform state in GCS
resource "google_storage_bucket_iam_member" "ci_tf_state_object_admin" {
  bucket = var.tf_state_bucket
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.ci.email}"
}

resource "google_storage_bucket_iam_member" "ci_tf_state_bucket_reader" {
  bucket = var.tf_state_bucket
  role   = "roles/storage.legacyBucketReader"
  member = "serviceAccount:${google_service_account.ci.email}"
}

# --- Workload Identity Federation for GitHub Actions ---

resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "github-actions-pool"
  display_name              = "GitHub Actions"

  depends_on = [google_project_service.apis]
}

resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-actions-provider"
  display_name                       = "GitHub Actions OIDC"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
  }

  # Only tokens from this exact repo can use this provider
  attribute_condition = "attribute.repository == '${var.github_repo}'"
}

# Bind the WIF pool principal to the CI service account
resource "google_service_account_iam_member" "ci_wif" {
  service_account_id = google_service_account.ci.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_repo}"
}
