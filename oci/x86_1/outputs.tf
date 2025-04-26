output "vcn_state" {
  description = "The state of the VCN."
  value       = oci_core_instance.generated_oci_core_instance.state
}

output "public_id" {
  description = "CIDR block of the core VCN"
  value       = oci_core_instance.generated_oci_core_instance.public_ip
}
