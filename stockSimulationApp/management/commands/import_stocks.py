import csv
from django.core.management.base import BaseCommand
from stockSimulationApp.models import StockData
from datetime import datetime

class Command(BaseCommand):
    help = "Import stock data from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")
        parser.add_argument("ticker", type=str, help="Company ticker")

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs["csv_file"]
        ticker = kwargs["ticker"]

        try:
            with open(csv_file_path, "r", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)

                # Debugging: Print column names from the CSV file
                reader.fieldnames = [name.strip().replace('"', '') for name in reader.fieldnames] 

                for row in reader:
                    row = {key.strip().replace('"', ''): value for key, value in row.items()}  # Ensure all keys are cleaned
                   
                    StockData.objects.update_or_create(
                        company_ticker=ticker,
                        date=datetime.strptime(row["Date"], "%m/%d/%Y").date(),
                             
                        defaults={
                            "price": float(row["Price"]),
                            "open_price": float(row["Open"]),
                            "high": float(row["High"]),
                            "low": float(row["Low"]),
                            "volume": row["Vol."],  # Keep as string if large
                            "change_percent": float(row["Change %"].strip("%")),
                        }
                    )

            self.stdout.write(self.style.SUCCESS(f"Stock data for {ticker} imported successfully!"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error importing data: {e}"))
