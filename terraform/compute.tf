data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}
resource "aws_key_pair" "terraform_key" {
  key_name   = "manga-list-terraform-key"
  public_key = file("~/.ssh/terraform-key.pub")
}
resource "aws_security_group" "manga_list_sg" {
  name   = "manga-list-sg"
  vpc_id = aws_vpc.main.id
  ingress {
    description = "SSH from my IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${var.my_ip}/32"]
  }
  ingress {
    description = "HTTP open to all"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { Name = "manga-list-sg" }
}
resource "aws_instance" "manga_list" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.manga_list_sg.id]
  key_name               = aws_key_pair.terraform_key.key_name
  tags = { Name = "manga-list-server" }
}
