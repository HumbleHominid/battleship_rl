resource "google_artifact_registry_repository" "app" {
  repository_id = "battleship-rl"
  location      = var.region
  format        = "DOCKER"

  cleanup_policies {
    id     = "keep-last-5"
    action = "KEEP"
    most_recent_versions {
      keep_count = 5
    }
  }

  cleanup_policy_dry_run = false

  depends_on = [google_project_service.apis]
}
