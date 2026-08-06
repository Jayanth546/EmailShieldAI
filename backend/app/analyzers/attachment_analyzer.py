import os


class AttachmentAnalyzer:
    DANGEROUS_EXTENSIONS = {
        ".exe",
        ".bat",
        ".cmd",
        ".js",
        ".vbs",
        ".scr",
        ".ps1",
    }

    MACRO_EXTENSIONS = {
        ".docm",
        ".xlsm",
        ".pptm",
    }

    ARCHIVE_EXTENSIONS = {
        ".zip",
        ".rar",
        ".7z",
    }

    def analyze(self, attachments):
        issues = []
        score = 0

        for filename in attachments:
            filename_lower = filename.lower()

            # Rule 1: Dangerous executable
            _, ext = os.path.splitext(filename_lower)

            if ext in self.DANGEROUS_EXTENSIONS:
                issues.append(
                    f"Dangerous executable attachment: {filename}"
                )
                score += 30

            # Rule 2: Double extension
            parts = filename_lower.split(".")

            if len(parts) >= 3:
                issues.append(
                    f"Double extension detected: {filename}"
                )
                score += 25

            # Rule 3: Macro-enabled Office file
            if ext in self.MACRO_EXTENSIONS:
                issues.append(
                    f"Macro-enabled Office document: {filename}"
                )
                score += 20

            # Rule 4: Archive file
            if ext in self.ARCHIVE_EXTENSIONS:
                issues.append(
                    f"Compressed archive attachment: {filename}"
                )
                score += 10

        return {
            "score": score,
            "issues": issues,
        }
