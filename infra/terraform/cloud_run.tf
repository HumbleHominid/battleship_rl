locals {
  ar_image_base = "${var.region}-docker.pkg.dev/${var.project_id}/battleship-rl/app"

  # Use a public placeholder on the initial apply (before the first CI deployment).
  # CI always passes image_tag=<git-sha>, replacing the placeholder.
  image = var.image_tag == "placeholder" ? "us-docker.pkg.dev/cloudrun/container/hello:latest" : "${local.ar_image_base}:${var.image_tag}"
}

resource "google_cloud_run_v2_service" "app" {
  name     = "battleship-rl"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.cloud_run.email

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }

    timeout = "3600s"

    containers {
      image = local.image

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "1024Mi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }
    }
  }

  depends_on = [
    google_project_service.apis,
    google_artifact_registry_repository.app,
  ]
}

resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  name     = google_cloud_run_v2_service.app.name
  location = google_cloud_run_v2_service.app.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
