# --- Virtual Cloud Network ---
resource "oci_core_vcn" "main" {
  compartment_id = var.compartment_ocid
  cidr_blocks    = [var.vcn_cidr]
  display_name   = "${var.project_name}-vcn"
  dns_label      = var.project_name

  freeform_tags = var.freeform_tags
}
# --- Internet Gateway (for public subnet) ---
resource "oci_core_internet_gateway" "main" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-igw"
  enabled        = true

  freeform_tags = var.freeform_tags
}
# --- NAT Gateway (for private subnet outbound internet) ---
resource "oci_core_nat_gateway" "main" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "${var.project_name}-natgw"

  freeform_tags = var.freeform_tags
}
# --- Public Route Table (routes to Internet Gateway) ---
resource "oci_core_route_table" "public" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "public-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_internet_gateway.main.id
  }

  freeform_tags = var.freeform_tags
}

# --- Private Route Table (routes to NAT Gateway) ---
resource "oci_core_route_table" "private" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "private-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_nat_gateway.main.id
  }

  freeform_tags = var.freeform_tags
}
# --- Public Security List ---
resource "oci_core_security_list" "public" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "public-sl"

  # Allow SSH from anywhere (in production, restrict to your IP)
  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 22
      max = 22
    }
  }

  # Allow all outbound traffic
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }

  freeform_tags = var.freeform_tags
}

# --- Private Security List ---
resource "oci_core_security_list" "private" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "private-sl"

  # SSH from public subnet only
  ingress_security_rules {
    protocol = "6" # TCP
    source   = var.public_subnet_cidr
    tcp_options {
      min = 22
      max = 22
    }
  }

  # App traffic from public subnet
  ingress_security_rules {
    protocol = "6" # TCP
    source   = var.public_subnet_cidr
    tcp_options {
      min = 8000
      max = 8000
    }
  }

  # Allow all outbound (for dnf, pip via NAT)
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }

  freeform_tags = var.freeform_tags
}
# --- Public Subnet ---
resource "oci_core_subnet" "public" {
  compartment_id    = var.compartment_ocid
  vcn_id            = oci_core_vcn.main.id
  cidr_block        = var.public_subnet_cidr
  display_name      = "public-subnet"
  dns_label         = "public"
  route_table_id    = oci_core_route_table.public.id
  security_list_ids = [oci_core_security_list.public.id]

  freeform_tags = var.freeform_tags
}

# --- Private Subnet ---
resource "oci_core_subnet" "private" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.main.id
  cidr_block                 = var.private_subnet_cidr
  display_name               = "private-subnet"
  dns_label                  = "private"
  route_table_id             = oci_core_route_table.private.id
  security_list_ids          = [oci_core_security_list.private.id]
  prohibit_public_ip_on_vnic = true

  freeform_tags = var.freeform_tags
}