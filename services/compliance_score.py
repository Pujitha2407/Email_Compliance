import json

class ComplainceScore:
    def __init__(self, user_config):
        self.risk_categories = {}
        for category, weight in user_config["categories"].items():
            self.risk_categories[category.lower()] = weight
        self.status = user_config["status"]
        self.scores = {}

    def calculate_score(self, emails_results):
        print("Calculating Score...")
        self.scores = {}
        for mail_id, result in emails_results.items():
            if "error" in result:
                self.scores[mail_id] = {
                    "classification": "Need Review",
                    "score": 0,
                    "status": "Low"
                }
                continue
            score = 0
            high_risk = 0
            for value in result["categories"]:
                category = value["category"].lower()
                if category in self.risk_categories:
                    category_score = self.risk_categories[category]
                    if category_score > high_risk:
                        high_risk = category_score
                    score += category_score
            score = high_risk + 0.2 * (score - high_risk)
            score = min(score, 100)
            classification = (
                "Non Compliant"
                if result["violation"] == True
                else "Compliant"
            )
            status = "Low"
            if score >= self.status["Critical"]:
                status = "Critical"
            elif score >= self.status["High"]:
                status = "High"
            elif score >= self.status["Medium"]:
                status = "Medium"
            self.scores[mail_id] = {
                "classification": classification,
                "score": score,
                "status": status
            }

    def generate_report(self, emails, emails_results):
        print("Generating Report...")
        report = {}
        for mail_id, email in emails.items():
            report[mail_id] = {
                "email": email,
                "risk_categories": emails_results.get(
                    mail_id,
                    {}
                ).get("categories",""),
                "classification": self.scores.get(
                    mail_id,
                    {}
                ).get("classification", ""),
                "score": self.scores.get(
                    mail_id,
                    {}
                ).get("score", 0),
                "status": self.scores.get(
                    mail_id,
                    {}
                ).get("status", "")
            }
        with open("report.json", "w") as f:
            json.dump(report, f, indent=4)
        print("Generate Report Finished.")

    def execute(self, emails, emails_results):
        print("Running Compliance Scoring...")
        self.calculate_score(emails_results)
        self.generate_report(emails, emails_results)