"""
Seed script — populates the database with realistic dummy data for frontend testing.
Run from the project root:  python seed.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from datetime import datetime, timezone
from sqlalchemy import Table, MetaData, text
from config.database import SessionLocal, engine, Base
from models.distributor import Distributor
from models.donor import Donor
from models.campaign import Campaign
from models.donation import Donation
from models.proof import Proof
from models.vote import Vote

# Reflect the legacy `users` table (FK target for campaigns + donations)
_meta = MetaData()
_meta.reflect(bind=engine, only=["users"])
UsersTable = _meta.tables["users"]

# ---------------------------------------------------------------------------
# Addresses
# ---------------------------------------------------------------------------

# Required distributor addresses (from the task)
DIST_ADDRESSES = [
    "0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65",
    "0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc",
    "0x976EA74026E726554dB657fA54763abd0C3a0aa9",
    "0x14dC79964da2C08b23698B3D3cc7Ca32193d9955",
    # Additional distributors
    "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
    "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
    "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
    "0x90F79bf6EB2c4f870365E785982E1f101E93b906",
]

DISTRIBUTOR_PROFILES = [
    {"first_name": "Ayesha", "last_name": "Khan",      "email": "ayesha.khan@blocharity.io",    "location": "Pakistan"},
    {"first_name": "Kofi",   "last_name": "Mensah",    "email": "kofi.mensah@blocharity.io",    "location": "Kenya"},
    {"first_name": "Priya",  "last_name": "Chowdhury", "email": "priya.chowdhury@blocharity.io","location": "Bangladesh"},
    {"first_name": "Dmytro", "last_name": "Kovalenko", "email": "dmytro.kovalenko@blocharity.io","location": "Ukraine"},
    {"first_name": "Maria",  "last_name": "Santos",    "email": "maria.santos@blocharity.io",   "location": "Philippines"},
    {"first_name": "Emeka",  "last_name": "Okafor",    "email": "emeka.okafor@blocharity.io",   "location": "Nigeria"},
    {"first_name": "Fatima", "last_name": "Al-Hassan",  "email": "fatima.alhassan@blocharity.io","location": "Somalia"},
    {"first_name": "Yuki",   "last_name": "Tanaka",    "email": "yuki.tanaka@blocharity.io",    "location": "Japan"},
]

DONOR_ADDRESSES = [
    "0xFABB0ac9d68B0B445fB7357272Ff202C5651694a",
    "0x1CBd3b2770909D4e10f157cABC84C7264073C9Ec",
    "0xdF3e18d64BC6A983f673Ab319CCaE4f1a57C7097",
    "0xcd3B766CCDd6AE721141F452C550Ca635964ce71",
    "0x2546BcD3c84621e976D8185a91A922aE77ECEc30",
    "0xbDA5747bFD65F08deb54cb465eB87D40e51B197E",
    "0xdD2FD4581271e230360230F9337D5c0430Bf44C0",
    "0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199",
]

DONOR_PROFILES = [
    {"first_name": "James",    "last_name": "Whitfield",  "email": "james.whitfield@mail.com",  "location": "United States"},
    {"first_name": "Sophie",   "last_name": "Marchand",   "email": "sophie.marchand@mail.com",  "location": "France"},
    {"first_name": "Ravi",     "last_name": "Nair",       "email": "ravi.nair@mail.com",        "location": "India"},
    {"first_name": "Laura",    "last_name": "Becker",     "email": "laura.becker@mail.com",     "location": "Germany"},
    {"first_name": "Chen",     "last_name": "Wei",        "email": "chen.wei@mail.com",         "location": "China"},
    {"first_name": "Fatou",    "last_name": "Diallo",     "email": "fatou.diallo@mail.com",     "location": "Senegal"},
    {"first_name": "Carlos",   "last_name": "Rivera",     "email": "carlos.rivera@mail.com",    "location": "Mexico"},
    {"first_name": "Amara",    "last_name": "Ibrahim",    "email": "amara.ibrahim@mail.com",    "location": "Sudan"},
]

# ---------------------------------------------------------------------------
# Campaign data
# ---------------------------------------------------------------------------

def dt(s):
    return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)

CAMPAIGNS = [
    # --- 0x15d34... (Ayesha Khan, Pakistan) ---
    {
        "id": 1,
        "distributor_address": DIST_ADDRESSES[0],
        "title": "Emergency Flood Relief – Sindh Province",
        "description": (
            "Catastrophic monsoon flooding has displaced over 200,000 families across Sindh. "
            "Funds will provide emergency food packs, tarpaulin shelters, and clean drinking water "
            "for the most severely affected households. Distribution begins within 48 hours of milestone."
        ),
        "location": "Pakistan",
        "category_name": "Weather Crisis",
        "milestone_amount": 100000,   # $1,000
        "current_amount": 12400,      # 12.4% — early stage (scenario 1)
        "status": 0,
        "activity_status": 0,
        "end_date": dt("2026-09-01T00:00:00"),
        "positive_votes": 0,
        "negative_votes": 0,
        "total_voters": 0,
    },
    {
        "id": 2,
        "distributor_address": DIST_ADDRESSES[0],
        "title": "Permanent Shelter for Flood-Displaced Families",
        "description": (
            "Following repeated flooding seasons, 500 families in rural Sindh still lack permanent housing. "
            "This campaign funded prefabricated home kits and skilled labour for construction. "
            "All units were delivered and verified — the campaign closed successfully."
        ),
        "location": "Pakistan",
        "category_name": "Shelter",
        "milestone_amount": 250000,   # $2,500
        "current_amount": 250000,     # fully funded (scenario 5)
        "status": 1,
        "activity_status": 4,
        "end_date": dt("2026-03-01T00:00:00"),
        "positive_votes": 18,
        "negative_votes": 2,
        "total_voters": 20,
    },

    # --- 0x9965... (Kofi Mensah, Kenya) ---
    {
        "id": 3,
        "distributor_address": DIST_ADDRESSES[1],
        "title": "Drought Food Aid – Turkana County",
        "description": (
            "A prolonged drought has left 60,000 people in Turkana facing acute food insecurity. "
            "Donations will purchase and transport sorghum, maize flour, and fortified porridge "
            "directly to distribution points run by local community leaders."
        ),
        "location": "Kenya",
        "category_name": "Food",
        "milestone_amount": 50000,    # $500
        "current_amount": 45800,      # 91.6% — nearly reached (scenario 2)
        "status": 0,
        "activity_status": 0,
        "end_date": dt("2026-07-15T00:00:00"),
        "positive_votes": 0,
        "negative_votes": 0,
        "total_voters": 0,
    },
    {
        "id": 4,
        "distributor_address": DIST_ADDRESSES[1],
        "title": "Clean Water Boreholes – Marsabit Region",
        "description": (
            "Communities in Marsabit walk up to six hours daily for contaminated water. "
            "This campaign drilled two boreholes and installed hand pumps serving 3,000 people. "
            "Proof of completion has been submitted and the community vote is now open."
        ),
        "location": "Kenya",
        "category_name": "Clean Water",
        "milestone_amount": 80000,    # $800
        "current_amount": 80000,      # fully funded
        "status": 0,
        "activity_status": 3,         # voting in progress (scenario 4)
        "end_date": dt("2026-05-20T00:00:00"),
        "positive_votes": 11,
        "negative_votes": 3,
        "total_voters": 14,
    },

    # --- 0x976E... (Priya Chowdhury, Bangladesh) ---
    {
        "id": 5,
        "distributor_address": DIST_ADDRESSES[2],
        "title": "Cyclone Mocha Recovery – Cox's Bazar",
        "description": (
            "Cyclone Mocha devastated coastal communities in Cox's Bazar, destroying fishing boats "
            "and livelihoods. Funds will replace boats, repair nets, and restore income for 120 "
            "fishing families so they can sustain themselves through the next season."
        ),
        "location": "Bangladesh",
        "category_name": "Weather Crisis",
        "milestone_amount": 60000,    # $600
        "current_amount": 60000,      # milestone reached, proof not yet uploaded (scenario 3)
        "status": 0,
        "activity_status": 1,
        "end_date": dt("2026-08-10T00:00:00"),
        "positive_votes": 0,
        "negative_votes": 0,
        "total_voters": 0,
    },
    {
        "id": 6,
        "distributor_address": DIST_ADDRESSES[2],
        "title": "Primary School Rebuilding – Sylhet District",
        "description": (
            "Flooding destroyed three primary schools in Sylhet, leaving 900 children without "
            "classrooms. This campaign was cancelled after the regional authority confirmed they "
            "would fund reconstruction through government grants, making charity funds unnecessary."
        ),
        "location": "Bangladesh",
        "category_name": "Education",
        "milestone_amount": 120000,   # $1,200
        "current_amount": 34000,
        "status": 2,                  # cancelled (scenario 6)
        "activity_status": 0,
        "end_date": dt("2026-06-30T00:00:00"),
        "positive_votes": 0,
        "negative_votes": 0,
        "total_voters": 0,
    },

    # --- 0x14dC... (Dmytro Kovalenko, Ukraine) ---
    {
        "id": 7,
        "distributor_address": DIST_ADDRESSES[3],
        "title": "Winter Heating Kits – Kharkiv Oblast",
        "description": (
            "With infrastructure severely damaged, thousands of households in Kharkiv are facing "
            "a winter without central heating. This campaign is purchasing and distributing "
            "portable wood-burning stoves, fuel, and thermal blankets to elderly residents."
        ),
        "location": "Ukraine",
        "category_name": "Weather Crisis",
        "milestone_amount": 200000,   # $2,000
        "current_amount": 31500,      # 15.75% — early stage (scenario 1 again, different dist)
        "status": 0,
        "activity_status": 0,
        "end_date": dt("2026-11-01T00:00:00"),
        "positive_votes": 0,
        "negative_votes": 0,
        "total_voters": 0,
    },
    {
        "id": 8,
        "distributor_address": DIST_ADDRESSES[3],
        "title": "Mobile Medical Clinics – Frontline Communities",
        "description": (
            "Three retrofitted vans now serve as mobile clinics visiting villages with no hospital "
            "access near the eastern frontline. The campaign reached its goal, funds were withdrawn, "
            "and the clinic programme ran for three months with full documentation submitted."
        ),
        "location": "Ukraine",
        "category_name": "Healthcare",
        "milestone_amount": 300000,   # $3,000
        "current_amount": 300000,
        "status": 1,                  # completed (scenario 5)
        "activity_status": 4,
        "end_date": dt("2026-02-01T00:00:00"),
        "positive_votes": 22,
        "negative_votes": 1,
        "total_voters": 23,
    },

    # --- Extra distributors ---
    {
        "id": 9,
        "distributor_address": DIST_ADDRESSES[4],  # Maria Santos, Philippines
        "title": "Typhoon Egay School Supplies – Isabela",
        "description": (
            "Typhoon Egay swept through Isabela province and destroyed classrooms and all learning "
            "materials in seven schools. Donations are covering replacement textbooks, notebooks, "
            "and basic stationery so 2,000 pupils can resume classes immediately."
        ),
        "location": "Philippines",
        "category_name": "Education",
        "milestone_amount": 40000,    # $400
        "current_amount": 36200,      # 90.5% — nearly reached (scenario 2)
        "status": 0,
        "activity_status": 0,
        "end_date": dt("2026-07-01T00:00:00"),
        "positive_votes": 0,
        "negative_votes": 0,
        "total_voters": 0,
    },
    {
        "id": 10,
        "distributor_address": DIST_ADDRESSES[4],  # Philippines
        "title": "Coastal Village Healthcare Outreach – Leyte",
        "description": (
            "Remote coastal villages in Leyte have no clinic within 40 km. "
            "This campaign funds quarterly visits by a medical team providing vaccinations, "
            "maternal care, and basic diagnostics. Proof of the first two visits has been uploaded."
        ),
        "location": "Philippines",
        "category_name": "Healthcare",
        "milestone_amount": 75000,
        "current_amount": 75000,
        "status": 0,
        "activity_status": 3,         # voting (scenario 4)
        "end_date": dt("2026-06-15T00:00:00"),
        "positive_votes": 9,
        "negative_votes": 4,
        "total_voters": 13,
    },
    {
        "id": 11,
        "distributor_address": DIST_ADDRESSES[5],  # Emeka Okafor, Nigeria
        "title": "Food Voucher Programme – Borno State",
        "description": (
            "Displaced families in Borno State are receiving monthly food vouchers redeemable at "
            "local markets, keeping money in the community economy while addressing hunger. "
            "The milestone has been reached and the team is preparing proof documentation."
        ),
        "location": "Nigeria",
        "category_name": "Food",
        "milestone_amount": 90000,
        "current_amount": 90000,      # milestone reached, awaiting proof (scenario 3)
        "status": 0,
        "activity_status": 1,
        "end_date": dt("2026-08-01T00:00:00"),
        "positive_votes": 0,
        "negative_votes": 0,
        "total_voters": 0,
    },
    {
        "id": 12,
        "distributor_address": DIST_ADDRESSES[6],  # Fatima Al-Hassan, Somalia
        "title": "Famine Response – Bay Region",
        "description": (
            "IPC Phase 4 famine conditions have been declared in Bay Region. "
            "This campaign is in early fundraising to purchase high-energy biscuits and therapeutic "
            "food for children under five showing signs of acute malnutrition."
        ),
        "location": "Somalia",
        "category_name": "Food",
        "milestone_amount": 500000,   # $5,000
        "current_amount": 48000,      # early stage (scenario 1)
        "status": 0,
        "activity_status": 0,
        "end_date": dt("2026-10-01T00:00:00"),
        "positive_votes": 0,
        "negative_votes": 0,
        "total_voters": 0,
    },
]

# proof for campaigns with activity_status >= 2
PROOFS = [
    {
        "campaign_id": 2,
        "ipfs_hash": "QmPK1s3pNYLi9ERiq3BDxKa4XosgWwFRQUydHUtz4YgpqB",
        "uploaded_by": DIST_ADDRESSES[0],
        "timestamp": dt("2026-02-20T10:30:00"),
    },
    {
        "campaign_id": 4,
        "ipfs_hash": "QmT4AeWhxgTs8ANkPmJKoQ7m3p8wbLtQEi7RJxwVGgx5JZ",
        "uploaded_by": DIST_ADDRESSES[1],
        "timestamp": dt("2026-05-01T08:15:00"),
    },
    {
        "campaign_id": 8,
        "ipfs_hash": "QmWnRy7Nm9X2QVvPEbbYo5cKhRaXHc8vKJrGfTXQ3YcLmD",
        "uploaded_by": DIST_ADDRESSES[3],
        "timestamp": dt("2026-01-25T14:00:00"),
    },
    {
        "campaign_id": 10,
        "ipfs_hash": "QmZrKcMvHuY8o1TbnB4jWxLpS6dRfNqXe7TgCsYtPaM3Vk",
        "uploaded_by": DIST_ADDRESSES[4],
        "timestamp": dt("2026-05-03T11:45:00"),
    },
]

# donations: (campaign_id, donor_index, amount_cents, tx_suffix)
DONATIONS_RAW = [
    # Campaign 1 – early active
    (1, 0, 2500,  "a1b2c3"), (1, 1, 3100,  "d4e5f6"), (1, 2, 1800,  "g7h8i9"),
    (1, 3, 5000,  "j0k1l2"),
    # Campaign 2 – completed (historical)
    (2, 0, 30000, "m3n4o5"), (2, 1, 50000, "p6q7r8"), (2, 2, 40000, "s9t0u1"),
    (2, 3, 60000, "v2w3x4"), (2, 4, 50000, "y5z6a7"), (2, 5, 20000, "b8c9d0"),
    # Campaign 3 – nearly reached
    (3, 1, 10000, "e1f2g3"), (3, 2, 12000, "h4i5j6"), (3, 3,  8000, "k7l8m9"),
    (3, 4, 15800, "n0o1p2"),
    # Campaign 4 – voting
    (4, 0, 20000, "q3r4s5"), (4, 1, 25000, "t6u7v8"), (4, 5, 15000, "w9x0y1"),
    (4, 6, 20000, "z2a3b4"),
    # Campaign 5 – milestone reached
    (5, 0, 15000, "c5d6e7"), (5, 2, 20000, "f8g9h0"), (5, 3, 25000, "i1j2k3"),
    # Campaign 7 – early active
    (7, 4, 12000, "l4m5n6"), (7, 5,  9500, "o7p8q9"), (7, 6, 10000, "r0s1t2"),
    # Campaign 8 – completed
    (8, 0, 80000, "u3v4w5"), (8, 1, 90000, "x6y7z8"), (8, 2, 70000, "a9b0c1"),
    (8, 3, 60000, "d2e3f4"),
    # Campaign 9 – nearly reached
    (9, 6, 10000, "g5h6i7"), (9, 7, 12000, "j8k9l0"), (9, 0, 14200, "m1n2o3"),
    # Campaign 10 – voting
    (10, 1, 20000, "p4q5r6"), (10, 2, 25000, "s7t8u9"), (10, 3, 15000, "v0w1x2"),
    (10, 4, 15000, "y3z4a5"),
    # Campaign 11 – milestone reached
    (11, 5, 30000, "b6c7d8"), (11, 6, 35000, "e9f0g1"), (11, 7, 25000, "h2i3j4"),
    # Campaign 12 – early active
    (12, 0, 15000, "k5l6m7"), (12, 1, 18000, "n8o9p0"), (12, 2, 15000, "q1r2s3"),
]

# votes: (campaign_id, donor_index, vote_bool, tx_suffix)
VOTES_RAW = [
    # Campaign 2 – completed, approved
    (2,  0, True,  "v001"), (2,  1, True,  "v002"), (2,  2, True,  "v003"),
    (2,  3, True,  "v004"), (2,  4, True,  "v005"), (2,  5, True,  "v006"),
    (2,  6, False, "v007"), (2,  7, True,  "v008"),
    # Campaign 4 – voting in progress
    (4,  0, True,  "v009"), (4,  1, True,  "v010"), (4,  2, True,  "v011"),
    (4,  3, True,  "v012"), (4,  4, True,  "v013"), (4,  5, False, "v014"),
    (4,  6, False, "v015"), (4,  7, True,  "v016"),
    # Campaign 8 – completed, approved
    (8,  0, True,  "v017"), (8,  1, True,  "v018"), (8,  2, True,  "v019"),
    (8,  3, True,  "v020"), (8,  4, True,  "v021"), (8,  5, False, "v022"),
    # Campaign 10 – voting in progress
    (10, 0, True,  "v023"), (10, 1, True,  "v024"), (10, 2, True,  "v025"),
    (10, 3, True,  "v026"), (10, 4, True,  "v027"), (10, 5, False, "v028"),
    (10, 6, False, "v029"), (10, 7, True,  "v030"),
]


def _upsert_user(conn, address, profile, is_distributor):
    exists = conn.execute(
        text("SELECT 1 FROM users WHERE address = :a"), {"a": address}
    ).first()
    if not exists:
        conn.execute(UsersTable.insert().values(
            address=address,
            first_name=profile["first_name"],
            last_name=profile["last_name"],
            email=profile["email"],
            location=profile["location"],
            is_distributor=is_distributor,
        ))


def seed():
    db = SessionLocal()
    try:
        # users table is the FK parent for campaigns.distributor_address
        # and donations.donor_address — seed it first using a raw connection
        print("Seeding users table...")
        with engine.begin() as conn:
            for addr, profile in zip(DIST_ADDRESSES, DISTRIBUTOR_PROFILES):
                _upsert_user(conn, addr, profile, True)
            for addr, profile in zip(DONOR_ADDRESSES, DONOR_PROFILES):
                _upsert_user(conn, addr, profile, False)

        print("Seeding distributors...")
        for addr, profile in zip(DIST_ADDRESSES, DISTRIBUTOR_PROFILES):
            if not db.query(Distributor).filter_by(address=addr).first():
                db.add(Distributor(
                    address=addr,
                    has_security_deposit=True,
                    **profile,
                ))
        db.flush()

        print("Seeding donors...")
        for addr, profile in zip(DONOR_ADDRESSES, DONOR_PROFILES):
            if not db.query(Donor).filter_by(address=addr).first():
                db.add(Donor(address=addr, **profile))
        db.flush()

        print("Seeding campaigns...")
        for c in CAMPAIGNS:
            if not db.query(Campaign).filter_by(id=c["id"]).first():
                db.add(Campaign(**c))
        db.flush()

        print("Seeding proofs...")
        for p in PROOFS:
            if not db.query(Proof).filter_by(
                campaign_id=p["campaign_id"], ipfs_hash=p["ipfs_hash"]
            ).first():
                db.add(Proof(**p))
        db.flush()

        print("Seeding donations...")
        for campaign_id, donor_idx, amount, tx_suffix in DONATIONS_RAW:
            tx_hash = f"0xdeed{campaign_id:04d}{donor_idx}{tx_suffix}"
            if not db.query(Donation).filter_by(tx_hash=tx_hash).first():
                db.add(Donation(
                    tx_hash=tx_hash,
                    campaign_id=campaign_id,
                    donor_address=DONOR_ADDRESSES[donor_idx],
                    amount=amount,
                ))
        db.flush()

        print("Seeding votes...")
        for campaign_id, donor_idx, vote_val, tx_suffix in VOTES_RAW:
            tx_hash = f"0xvote{campaign_id:04d}{donor_idx}{tx_suffix}"
            if not db.query(Vote).filter_by(tx_hash=tx_hash).first():
                db.add(Vote(
                    tx_hash=tx_hash,
                    campaign_id=campaign_id,
                    voter_address=DONOR_ADDRESSES[donor_idx],
                    vote=vote_val,
                ))

        print("Updating active_campaign_id for distributors...")
        active_map = {
            DIST_ADDRESSES[0]: 1,   # campaign 1 is active
            DIST_ADDRESSES[1]: 3,   # campaign 3 is active
            DIST_ADDRESSES[2]: 5,   # campaign 5 is active
            DIST_ADDRESSES[3]: 7,   # campaign 7 is active
            DIST_ADDRESSES[4]: 9,   # campaign 9 is active
            DIST_ADDRESSES[5]: 11,  # campaign 11 is active
            DIST_ADDRESSES[6]: 12,  # campaign 12 is active
        }
        for addr, campaign_id in active_map.items():
            dist = db.query(Distributor).filter_by(address=addr).first()
            if dist:
                dist.active_campaign_id = campaign_id

        print("Updating donor total_donated_wei...")
        donor_totals = {}
        for campaign_id, donor_idx, amount, _ in DONATIONS_RAW:
            addr = DONOR_ADDRESSES[donor_idx]
            donor_totals[addr] = donor_totals.get(addr, 0) + amount
        for addr, total in donor_totals.items():
            donor = db.query(Donor).filter_by(address=addr).first()
            if donor:
                donor.total_donated_wei = total

        db.commit()
        print("\nDone — seed complete.")
        print(f"  Distributors : {len(DIST_ADDRESSES)}")
        print(f"  Donors       : {len(DONOR_ADDRESSES)}")
        print(f"  Campaigns    : {len(CAMPAIGNS)}")
        print(f"  Proofs       : {len(PROOFS)}")
        print(f"  Donations    : {len(DONATIONS_RAW)}")
        print(f"  Votes        : {len(VOTES_RAW)}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
