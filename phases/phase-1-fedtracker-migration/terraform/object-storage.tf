data "oci_objectstorage_namespace" "ns" {
  compartment_id = var.tenancy_ocid
}

resource "oci_objectstorage_bucket" "audit_evidence" {
  compartment_id = var.compartment_ocid
  namespace      = data.oci_objectstorage_namespace.ns.namespace
  name           = "audit-evidence"
  access_type    = "NoPublicAccess"
  versioning     = "Enabled"
  metadata       = { source = "fedtracker", lifecycle = "30d" }
}

resource "oci_objectstorage_bucket" "audit_evidence_processed" {
  compartment_id = var.compartment_ocid
  namespace      = data.oci_objectstorage_namespace.ns.namespace
  name           = "audit-evidence-processed"
  access_type    = "NoPublicAccess"
}
