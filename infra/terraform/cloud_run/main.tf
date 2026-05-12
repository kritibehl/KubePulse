terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

variable "project_id" {}
variable "region" {
  default = "us-central1"
}
variable "service_name" {
  default = "kubepulse"
}
variable "image" {
  description = "Container image for KubePulse"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_cloud_run_v2_service" "kubepulse" {
  name     = var.service_name
  location = var.region

  template {
    containers {
      image = var.image

      ports {
        container_port = 8000
      }

      env {
        name  = "KUBEPULSE_ENV"
        value = "cloud-run"
      }
    }
  }
}

output "service_uri" {
  value = google_cloud_run_v2_service.kubepulse.uri
}
