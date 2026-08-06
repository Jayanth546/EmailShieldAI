from app.parsers.email_parser import EmailParser


def main():
    parser = EmailParser("app/sample_emails/sample.eml")
    email = parser.parse()

    print("\n===== Parsed Email =====")

    for key, value in email.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
