# --- Authentication ---
variable "tenancy_ocid" {
  description = "OCID of the OCI tenancy"
  type        = string
}

variable "user_ocid" {
  description = "OCID of the OCI user"
  type        = string
}

variable "fingerprint" {
  description = "Fingerprint of the API key"
  type        = string
}

variable "private_key_path" {
  description = "Path to the OCI API private key file"
  type        = string
}

variable "region" {
  description = "OCI region (e.g., us-ashburn-1)"
  type        = string
  default     = "us-ashburn-1"
}

# --- Compartment ---
variable "compartment_ocid" {
  description = "OCID of the compartment to create resources in"
  type        = string
}

# --- Naming ---
variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "fedtracker"
}

variable "environment" {
  description = "Environment (lab, dev, staging, prod)"
  type        = string
  default     = "lab"
}

# --- Network ---
variable "vcn_cidr" {
  description = "CIDR block for the VCN"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "private_subnet_cidr" {
  description = "CIDR block for the private subnet"
  type        = string
  default     = "10.0.2.0/24"
}

# --- Compute ---
variable "instance_shape" {
  description = "Shape for compute instances (Always Free: VM.Standard.A1.Flex)"
  type        = string
  default     = "VM.Standard.A1.Flex"
}

variable "bastion_ocpus" {
  description = "Number of OCPUs for the bastion"
  type        = number
  default     = 1
}

variable "bastion_memory_gb" {
  description = "Memory in GB for the bastion"
  type        = number
  default     = 6
}

variable "app_server_ocpus" {
  description = "Number of OCPUs for the app server"
  type        = number
  default     = 1
}

variable "app_server_memory_gb" {
  description = "Memory in GB for the app server"
  type        = number
  default     = 10
}

variable "ssh_public_key_path" {
  description = "Path to the SSH public key for instance access"
  type        = string
}

variable "oracle_linux_image_id" {
  description = "OCID of the Oracle Linux image (region-specific, use OL9 for A1 Flex)"
  type        = string
}

# --- Tags ---
variable "freeform_tags" {
  description = "Freeform tags to apply to all resources"
  type        = map(string)
  default = {
    "Project"     = "fedtracker"
    "Environment" = "lab"
    "Owner"       = "btechk"
    "CostCenter"  = "interview-prep"
  }
}
