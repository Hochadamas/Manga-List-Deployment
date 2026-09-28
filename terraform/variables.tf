variable "aws_region" {
  type    = string
  default = "ap-northeast-1"
}
variable "vpc_cidr" {
  type    = string
  default = "10.1.0.0/16"
}
variable "subnet_cidr" {
  type    = string
  default = "10.1.1.0/24"
}
variable "instance_type" {
  type    = string
  default = "t3.micro"
}
variable "my_ip" {
  type = string
}
