# --- Outputs ---
output "bastion_public_ip" {
  description = "Public IP of the bastion host"
  value       = oci_core_instance.bastion.public_ip
}

output "app_server_private_ip" {
  description = "Private IP of the app server"
  value       = oci_core_instance.app_server.private_ip
}

output "vcn_id" {
  description = "OCID of the VCN"
  value       = oci_core_vcn.main.id
}

output "ssh_command_bastion" {
  description = "SSH command to connect to bastion"
  value       = "ssh -i ~/.ssh/fedtracker opc@${oci_core_instance.bastion.public_ip}"
}

output "ssh_command_app_server" {
  description = "SSH command to connect to app server through bastion"
  value       = "ssh -i ~/.ssh/fedtracker -J opc@${oci_core_instance.bastion.public_ip} opc@${oci_core_instance.app_server.private_ip}"
}