# Manga List

## 概要

このプロジェクトは、自分の漫画コレクションを管理するためのWebアプリケーションです。Flaskで開発したアプリケーションをDockerでコンテナ化し、TerraformでAWS上のインフラを構築してデプロイしています。

## Overview

A personal web app to track and manage a manga collection, built with Flask and SQLite. The application is containerized with Docker and deployed on AWS using Terraform for Infrastructure as Code.

This project builds on the DevOps toolchain explored in [Gitea-Infra-Deployment](https://github.com/Hochadamas/Gitea-Infra-Deployment), applying Terraform and Docker to a real application of my own.

## Features

- CRUD operations: add, edit, delete manga entries
- Search by title or author
- Cover image upload with automatic cleanup on deletion
- Server-side validation (Regex)

## Architecture

VPC (10.1.0.0/16)
└── Public subnet (10.1.1.0/24)
└── EC2: Flask app (Docker container, Gunicorn) + SQLite


The instance is reachable via SSH only from a restricted IP, and via HTTP on port 80. Data (SQLite database, uploaded images) persists on the host through Docker bind mounts, surviving container rebuilds and restarts.

## Tech stack

- **Backend**: Python, Flask, Gunicorn
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, Jinja2
- **Containerization**: Docker, Docker Compose
- **Infrastructure as Code**: Terraform
- **Cloud provider**: AWS (VPC, EC2, Security Groups)

## Deployment

```bash
cd terraform
terraform init
terraform plan -var="my_ip=YOUR_IP_ADDRESS"
terraform apply -var="my_ip=YOUR_IP_ADDRESS"
```

Once the instance is up, deploy the app:

```bash
git clone https://github.com/Hochadamas/Manga-List.git
cd Manga-List
touch mangas.db
docker compose up -d --build
```

## Project status

Application and Dockerization complete. Terraform infrastructure complete. Ansible deployment automation in progress.

## License

MIT