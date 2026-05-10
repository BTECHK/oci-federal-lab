# OCI API Gateway for FedTracker external traffic.
#
# Architecture: external clients → API Gateway → fedtracker-app on private subnet.
# JWT validation, rate limiting, CORS, and audit logging happen at the edge so the
# backend stays compliance-focused. See adrs/ADR-015-api-gateway-vs-direct-exposure.md.

variable "tenancy_ocid" {
  type        = string
  description = "OCI tenancy OCID."
}

variable "compartment_ocid" {
  type        = string
  description = "Compartment that owns the gateway."
}

variable "region" {
  type        = string
  description = "OCI region (e.g. us-ashburn-1)."
}

variable "public_subnet_id" {
  type        = string
  description = "OCID of the public subnet hosting the gateway."
}

variable "fedtracker_backend_url" {
  type        = string
  description = "Internal URL where fedtracker-app listens (e.g. http://10.0.2.201:8000)."
}

variable "jwt_issuers" {
  type        = list(string)
  description = "Allowed JWT issuers (one entry per OIDC IdP)."
}

variable "jwt_audiences" {
  type        = list(string)
  description = "Allowed JWT audiences (typically the gateway hostname)."
}

variable "jwks_uri" {
  type        = string
  description = "OIDC JWKS URI used to verify signatures."
}

variable "audit_log_group_id" {
  type        = string
  description = "OCID of the OCI Logging log group where access logs land."
}

variable "cors_allowed_origins" {
  type        = list(string)
  default     = ["https://*.fedplatform.gov"]
  description = "Origins allowed by CORS policy."
}

resource "oci_apigateway_gateway" "fedplatform" {
  compartment_id = var.compartment_ocid
  endpoint_type  = "PUBLIC"
  subnet_id      = var.public_subnet_id
  display_name   = "fedplatform-api-gateway"

  freeform_tags = {
    "phase"     = "P3"
    "ownership" = "fedplatform"
  }
}

resource "oci_apigateway_deployment" "fedplatform" {
  compartment_id = var.compartment_ocid
  display_name   = "fedplatform-v1"
  gateway_id     = oci_apigateway_gateway.fedplatform.id
  path_prefix    = "/v1"

  specification {
    request_policies {
      cors {
        allowed_origins = var.cors_allowed_origins
        allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        allowed_headers = ["Authorization", "Content-Type", "X-Trace-Id"]
        max_age_in_seconds = 3600
      }

      rate_limiting {
        rate_in_requests_per_second = 100
        rate_key                    = "CLIENT_IP"
      }

      authentication {
        type                        = "JWT_AUTHENTICATION"
        is_anonymous_access_allowed = false
        token_header                = "Authorization"
        token_auth_scheme           = "Bearer"
        issuers                     = var.jwt_issuers
        audiences                   = var.jwt_audiences

        public_keys {
          type           = "REMOTE_JWKS"
          uri            = var.jwks_uri
          max_cache_duration_in_hours = 1
          is_ssl_verify_disabled      = false
        }
      }
    }

    logging_policies {
      access_log {
        is_enabled = true
      }
      execution_log {
        is_enabled = true
        log_level  = "INFO"
      }
    }

    routes {
      path    = "/personnel/{id*}"
      methods = ["GET", "POST", "PUT", "DELETE"]
      backend {
        type = "HTTP_BACKEND"
        url  = "${var.fedtracker_backend_url}/personnel/$${request.path[id]}"
      }
    }

    routes {
      path    = "/audit/{action*}"
      methods = ["GET", "POST"]
      backend {
        type = "HTTP_BACKEND"
        url  = "${var.fedtracker_backend_url}/audit/$${request.path[action]}"
      }
    }

    routes {
      path    = "/compliance/{path*}"
      methods = ["GET", "POST"]
      backend {
        type = "HTTP_BACKEND"
        url  = "${var.fedtracker_backend_url}/compliance/$${request.path[path]}"
      }
    }
  }
}

output "gateway_hostname" {
  value       = oci_apigateway_gateway.fedplatform.hostname
  description = "Public hostname of the API Gateway. Use this for the JWT audience."
}

output "deployment_id" {
  value       = oci_apigateway_deployment.fedplatform.id
  description = "OCID of the v1 deployment."
}
