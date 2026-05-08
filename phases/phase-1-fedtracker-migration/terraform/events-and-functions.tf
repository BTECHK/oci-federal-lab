resource "oci_events_rule" "audit_evidence_created" {
  compartment_id = var.compartment_ocid
  display_name   = "audit-evidence-object-created"
  is_enabled     = true

  condition = jsonencode({
    eventType = ["com.oraclecloud.objectstorage.createobject"]
    data = {
      additionalDetails = {
        bucketName = ["audit-evidence"]
      }
    }
  })

  actions {
    actions {
      action_type = "FAAS"
      function_id = var.audit_processor_function_id
      is_enabled  = true
    }
  }
}

resource "oci_identity_policy" "audit_processor_fn_policies" {
  compartment_id = var.tenancy_ocid
  name           = "audit-processor-fn-policies"
  description    = "Resource principal policy for the audit-processor Function"
  statements = [
    "Allow any-user to use functions-family in compartment id ${var.compartment_ocid} where ALL { request.principal.type='servicecode', request.principal.servicename='objectstorage' }",
    "Allow resource id ${var.audit_processor_function_id} to read objects in compartment id ${var.compartment_ocid} where target.bucket.name = 'audit-evidence'",
    "Allow resource id ${var.audit_processor_function_id} to manage objects in compartment id ${var.compartment_ocid} where target.bucket.name = 'audit-evidence-processed'",
  ]
}
