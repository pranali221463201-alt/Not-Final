import time
import random

from plastic_inherent_risk.service import process_inherent_risk


# Curated demo news events with location tags
SIMULATED_NEWS_EVENTS_MUMBAI = [
    "[Mumbai] Explosion at BASF polymer production facility near Port",
    "[Mumbai] Chemical leak reported at BASF facility during maintenance shutdown",
    "[Mumbai] Fire damages polypropylene production line at Mumbai plant",
    "[Mumbai] Cooling system failure halts polymer extrusion unit",
    "[Mumbai] Safety incident reported at resin packaging facility in Navi Mumbai",
    "[Mumbai] Dow chemical plant reports operational disruption affecting polymer output",
    "[Mumbai] Labor strike disrupts polyethylene shipments from major supplier",
    "[Mumbai] Maintenance shutdown impacts polymer production capacity",
    "[Mumbai] Regulatory inspection launched after safety concerns at plastics manufacturing",
    "[Mumbai] Supply chain disruption reported due to industrial accident at polymer plant in Maharashtra"
]

SIMULATED_NEWS_EVENTS_BHOPAL = [
    "[Bhopal] Explosion at plastics manufacturing plant affecting production",
    "[Bhopal] Chemical leak reported at polymer facility during maintenance",
    "[Bhopal] Fire damages polypropylene production line at Bhopal facility",
    "[Bhopal] Cooling system failure halts polymer production unit",
    "[Bhopal] Safety incident reported at polymer packaging facility",
    "[Bhopal] Major supplier reports operational disruption in Madhya Pradesh",
    "[Bhopal] Labor dispute impacts polymer shipments from facility",
    "[Bhopal] Scheduled maintenance affects polymer production capacity",
    "[Bhopal] Regulatory inspection launched after safety concerns",
    "[Bhopal] Supply chain disruption due to industrial incident in Bhopal region"
]


def start_news_simulator():

    print("✓ Real-time location-based news simulator started")

    while True:
        # Randomly select location
        location = random.choice(['Mumbai', 'Bhopal'])
        
        if location == 'Mumbai':
            news = random.choice(SIMULATED_NEWS_EVENTS_MUMBAI)
        else:
            news = random.choice(SIMULATED_NEWS_EVENTS_BHOPAL)

        print(f"[SIMULATED NEWS] {news}")

        try:
            process_inherent_risk(news, None)
        except Exception as e:
            print(f"News simulation error: {e}")

        # Wait before next news event
        time.sleep(30)