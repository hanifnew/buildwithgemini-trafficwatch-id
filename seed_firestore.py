import datetime
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-e50049ae2385"
COLLECTION_NAME = "traffic_alerts"

def seed_data():
    db = firestore.Client(project=PROJECT_ID)
    print(f"Connecting to Firestore for project {PROJECT_ID}...")

    alerts = [
        {
            "id": "alert-jkt-001",
            "title": "Penutupan Jalur MRT & TransJakarta Koridor 1",
            "location": "Jl. MH Thamrin - Bundaran HI",
            "type": "construction",
            "severity": "high",
            "status": "active",
            "description": "Pekerjaan konstruksi lanjutan MRT fase 2A menyebabkan penyempitan lajur dan rekayasa lalu lintas di simpang Bundaran HI.",
            "alternate_routes": ["Jl. KH Mas Mansyur", "Jl. HR Rasuna Said"],
            "affected_transit": ["TransJakarta Koridor 1", "MRT Bundaran HI"],
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        {
            "id": "alert-jkt-002",
            "title": "Genangan Air Pasca Hujan Deras",
            "location": "Jl. Kemang Raya, Jakarta Selatan",
            "type": "weather",
            "severity": "medium",
            "status": "active",
            "description": "Genangan air setinggi 20-30 cm terpantau di depan Pasar Jagal Kemang, kendaraan roda 2 diimbau mencari jalur alternatif.",
            "alternate_routes": ["Jl. Pangeran Antasari", "Jl. Bangka Raya"],
            "affected_transit": ["Mikrotrans JAK-31"],
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        {
            "id": "alert-jkt-003",
            "title": "Penerapan Rekayasa Ganjil-Genap & Pengalihan Arus KTT",
            "location": "Jl. Gatot Subroto - Semanggi",
            "type": "regulation",
            "severity": "high",
            "status": "active",
            "description": "Pemberlakuan pengalihan arus sementara di sekitar Semanggi menuju Kuningan terkait agenda delegasi.",
            "alternate_routes": ["Tol Dalam Kota (Cawang-Pluit)", "Jl. Wolter Monginsidi"],
            "affected_transit": ["TransJakarta Koridor 9"],
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
        {
            "id": "alert-jkt-004",
            "title": "Perbaikan Pipa Air PDAM",
            "location": "Jl. D.I. Panjaitan, Cawang",
            "type": "maintenance",
            "severity": "low",
            "status": "resolved",
            "description": "Pekerjaan darurat galian pipa telah selesai, arus lalu lintas kembali lancar secara bertahap.",
            "alternate_routes": ["Jl. Otista Raya"],
            "affected_transit": [],
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    ]

    for item in alerts:
        doc_id = item["id"]
        db.collection(COLLECTION_NAME).document(doc_id).set(item)
        print(f"Seeded document: {doc_id} -> {item['title']}")

    print("Firestore seeding complete!")

if __name__ == "__main__":
    seed_data()
