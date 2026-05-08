resource "oci_identity_dynamic_group" "fedtracker_instances" {
  compartment_id = var.tenancy_ocid
  name           = "fedtracker-instances"
  description    = "FedTracker app servers — write audit CSVs to Object Storage via Instance Principal"
  matching_rule  = "instance.compartment.id = '${var.compartment_ocid}'"
}

resource "oci_identity_policy" "fedtracker_instance_policies" {
  compartment_id = var.tenancy_ocid
  name           = "fedtracker-instance-policies"
  description    = "FedTracker VM permissions for audit export pipeline"
  statements = [
    "Allow dynamic-group fedtracker-instances to manage objects in compartment id ${var.compartment_ocid} where target.bucket.name = 'audit-evidence'",
    "Allow dynamic-group fedtracker-instances to read buckets in compartment id ${var.compartment_ocid}",
  ]
}
