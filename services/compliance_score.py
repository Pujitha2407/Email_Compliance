import json

class ComplainceScore:
    def __init__(self, user_config):
        self.risk_categories = user_config["categories"]
        self.threshold = user_config.get("threshold", 50)  # Default threshold is 50 if not specified

    def calculate_score(self, emails_results):
        print("Calculating Score...")
        self.scores = {}
        for mail_id, result in emails_results.items():
            if "error" in result:
                self.scores[mail_id] = {"score": 0, "status": "Human Review"}
                continue
            score = 0
            high_risk = 0
            for value in result["categories"]:
                if value["category"] in self.risk_categories:
                    if self.risk_categories[value["category"]] > high_risk:
                        high_risk = self.risk_categories[value["category"]]
                    score += self.risk_categories[value["category"]]
            score = high_risk + 0.2*(score - high_risk)
            score = min(score, 100)  # Ensure score does not exceed 100
            status = "Non Compliant" if score >= self.threshold else "Compliant"
            self.scores[mail_id] = {"score": score, "status": status}

    def generate_report(self, emails, emails_results):
        print("Generating Report...")
        # generate a report in json format combining mail, mail result, and score
        # and, output the report to a json file
        report = {}
        for mail_id, email in emails.items():
            report[mail_id] = {
                "email": email,
                "result": emails_results.get(mail_id, {}),
                "score": self.scores.get(mail_id, {})
            }
        with open("report.json", "w") as f:
            json.dump(report, f, indent=4)
        print("Generate Report Finished.")

    def execute(self, emails, emails_results):
        print("Running Compliance Scoring...")
        self.calculate_score(emails_results)
        self.generate_report(emails, emails_results)