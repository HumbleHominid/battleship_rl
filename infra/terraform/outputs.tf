output "cloud_run_url" {
  description = "Public URL of the Cloud Run service"
  value       = google_cloud_run_v2_service.app.uri
}

output "artifact_registry_repo" {
  description = "Full image path prefix (append :tag)"
  value       = local.ar_image_base
}

output "wif_provider" {
  description = "Workload Identity Federation provider — add this to GitHub secret WIF_PROVIDER"
  value       = google_iam_workload_identity_pool_provider.github.name
}

output "ci_service_account" {
  description = "CI service account email — add this to GitHub secret WIF_SERVICE_ACCOUNT"
  value       = google_service_account.ci.email
}
