# --- Data Sources ---
# Get the list of availability domains
data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}
# --- Bastion VM (public subnet) ---
resource "oci_core_instance" "bastion" {
  compartment_id      = var.compartment_ocid
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  display_name        = "bastion"
  shape               = var.instance_shape

  shape_config {
    ocpus         = var.bastion_ocpus
    memory_in_gbs = var.bastion_memory_gb
  }

  source_details {
    source_type = "image"
    source_id   = var.oracle_linux_image_id
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.public.id
    assign_public_ip = true
    display_name     = "bastion-vnic"
  }

  metadata = {
    ssh_authorized_keys = file(var.ssh_public_key_path)
  }

  freeform_tags = var.freeform_tags
}
# --- App Server VM (private subnet) ---
resource "oci_core_instance" "app_server" {
  compartment_id      = var.compartment_ocid
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  display_name        = "app-server"
  shape               = var.instance_shape

  shape_config {
    ocpus         = var.app_server_ocpus
    memory_in_gbs = var.app_server_memory_gb
  }

  source_details {
    source_type = "image"
    source_id   = var.oracle_linux_image_id
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.private.id
    assign_public_ip = false
    display_name     = "app-server-vnic"
  }

  metadata = {
    ssh_authorized_keys = file(var.ssh_app_public_key_path)
  }

  freeform_tags = var.freeform_tags
}