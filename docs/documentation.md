# 📚 Gamebless Backend — API Documentation

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** Firebase JWT (Bearer Token) — diperlukan di semua endpoint kecuali yang ditandai `[No Auth]`  
**Response Format:** Semua response menggunakan wrapper:
```json
{
  "status": "success" | "error",
  "message": "...",
  "data": { ... }
}
```

---

## 🏥 Health

### `GET /health`
> [No Auth] Cek status server.

**Response:**
```json
{ "status": "ok" }
```

---

## 🔐 Auth

### `POST /auth/sync`
> Dipanggil **sekali** saat pertama kali user login via Google (Firebase Auth).  
> Membuat dokumen user minimal di Firestore. Jika sudah ada, kembalikan profil yang ada tanpa overwrite.

**Header:** `Authorization: Bearer <firebase_id_token>`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response `200`:**
```json
{
  "status": "success",
  "message": "User synced successfully",
  "data": {
    "is_new_user": true,
    "profile": {
      "uid": "firebase_uid",
      "email": "user@example.com",
      "username": null,
      "full_name": null,
      "birth_date": null,
      "gender": null,
      "occupation": null,
      "avatar_url": null
    },
    "account_stats": {
      "total_points": 0,
      "current_streak": 0,
      "join_date": "2025-01-01T00:00:00"
    }
  }
}
```

---

## 👤 Users

### `GET /users/me`
> Mengambil profil lengkap + stats user. Dipanggil saat app launch untuk render info user.

**Header:** `Authorization: Bearer <firebase_id_token>`

**Response `200`:**
```json
{
  "status": "success",
  "message": "User fetched successfully",
  "data": {
    "profile": {
      "uid": "firebase_uid",
      "email": "user@example.com",
      "username": "dimas123",
      "full_name": "Dimas Saputra",
      "birth_date": "1998-05-10T00:00:00",
      "gender": "male",
      "occupation": "Software Engineer",
      "avatar_url": "https://..."
    },
    "account_stats": {
      "total_points": 150,
      "current_streak": 7,
      "join_date": "2025-01-01T00:00:00"
    }
  }
}
```

---

### `PUT /users/me`
> Update field profil user. Hanya field yang disertakan yang akan diperbarui (partial update).

**Header:** `Authorization: Bearer <firebase_id_token>`

**Request Body (semua opsional):**
```json
{
  "username": "dimas123",
  "full_name": "Dimas Saputra",
  "birth_date": "1998-05-10T00:00:00",
  "gender": "male",
  "occupation": "Software Engineer",
  "avatar_url": "https://..."
}
```

> **Gender values:** `"male"` | `"female"` | `"prefer_not_to_say"`

**Response `200`:**
```json
{
  "status": "success",
  "message": "Profile updated successfully",
  "data": {
    "uid": "firebase_uid",
    "email": "user@example.com",
    "username": "dimas123",
    "full_name": "Dimas Saputra",
    ...
  }
}
```

---

### `POST /users/attempts`
> Dipanggil frontend ketika `/domains/check` mengembalikan `is_blocked: true`.  
> Menginkrementasi `access_attempts_count` dan mereset streak jika percobaan pertama hari ini.

**Header:** `Authorization: Bearer <firebase_id_token>`

**Request Body:**
```json
{
  "url": "https://bet-site.com"
}
```

**Response `200`:**
```json
{
  "status": "success",
  "message": "Attempt recorded",
  "data": {
    "access_attempts_count": 1,
    "current_streak": 0
  }
}
```

---

### `GET /users/progress-report`
> Laporan progress lengkap dari `join_date` (maksimal `MAX_REPORT_DAYS` hari).

**Header:** `Authorization: Bearer <firebase_id_token>`

**Response `200`:**
```json
{
  "status": "success",
  "message": "Progress report fetched",
  "data": {
    "highest_streak": 14,
    "current_streak": 7,
    "total_days": 30,
    "is_capped": false,
    "cap_days": null,
    "daily_progress": [ ... ]
  }
}
```

---

## 🏆 Challenges

### `GET /challenges`
> Mengembalikan semua challenge dengan status `is_completed` berdasarkan progress hari ini.

**Header:** `Authorization: Bearer <firebase_id_token>`

**Response `200`:**
```json
{
  "status": "success",
  "message": "Challenges fetched",
  "data": {
    "challenges": [
      {
        "task_id": "menara_eiffel_tumbuh",
        "type": "funfact",
        "point_value": 25,
        "title": "Menara Eiffel yang Tumbuh",
        "description": "Menara Eiffel di Paris ternyata \"tumbuh\" setiap musim panas...",
        "image_url": "https://resort.co.id/menara-eiffel-destinasi-wisata-terpopuler-di-prancis/",
        "video_url": null,
        "article_url": null,
        "category": null,
        "question": "Dimana letak menara eiffel",
        "options": ["Pogung", "Klebengan", "Paris"],
        "correct_answers": 2,
        "is_completed": false
      }
    ],
    "total": 1
  }
}
```

---

### `POST /challenges/{task_id}/complete`
> Menandai challenge sebagai selesai. Deduplication mencegah point farming.  
> Memberikan poin ke `account_stats.total_points` secara atomik.

**Header:** `Authorization: Bearer <firebase_id_token>`

**Path Param:** `task_id` (string) — ID challenge, misal: `"menara_eiffel_tumbuh"`

**Response `200`:**
```json
{
  "status": "success",
  "message": "Challenge completed",
  "data": {
    "task_id": "menara_eiffel_tumbuh",
    "points_awarded": 25,
    "total_points": 185
  }
}
```

---

### `GET /challenges/history`
> Semua challenge yang pernah diselesaikan + total_points dari `account_stats`.

**Header:** `Authorization: Bearer <firebase_id_token>`

**Response `200`:**
```json
{
  "status": "success",
  "message": "Challenge history fetched",
  "data": {
    "completed_challenges": [
      {
        "task_id": "menara_eiffel_tumbuh",
        "type": "funfact",
        "points_awarded": 25,
        "completed_at": "2025-01-10T08:00:00"
      }
    ],
    "total_points": 185,
    "total_completed": 1
  }
}
```

---

## 🔒 Domains

### `GET /domains/check`
> [No Auth] Cek apakah URL termasuk situs judi.  
> 1. Exact match Firestore → blocked  
> 2. Vector similarity ≥ 0.90 → blocked + disimpan  
> 3. Selain itu → not blocked

**Query Param:** `url` (string) — URL yang dicek, misal: `?url=bet-site.com`

**Response `200`:**
```json
{
  "status": "success",
  "message": "Domain checked successfully",
  "data": {
    "url": "bet-site.com",
    "is_blocked": true
  }
}
```

---

### `POST /domains/report`
> [No Auth] User melaporkan situs yang dicurigai sebagai judi.  
> **Return langsung** (async). Analisis berjalan di background.

**Request Body:**
```json
{
  "url": "https://suspicious-site.com"
}
```

**Response `200`:**
```json
{
  "status": "success",
  "message": "Report received, domain will be analyzed",
  "data": {
    "url": "https://suspicious-site.com"
  }
}
```

---

## 💬 Chat

### `POST /chat/send`
> Kirim pesan ke AI psychologist.  
> Response AI datang via **Firestore listener** (StreamBuilder) — bukan dari response endpoint ini.

**Header:** `Authorization: Bearer <firebase_id_token>`

**Request Body:**
```json
{
  "message": "Aku merasa ingin berjudi lagi hari ini",
  "session_id": null
}
```

> `session_id: null` → buat sesi baru

**Response `200`:**
```json
{
  "status": "success",
  "message": "Chat send endpoint ready",
  "data": null
}
```

> ⚠️ **Note:** Endpoint ini masih dalam tahap `TODO`. ChatService belum diimplementasikan.

---

## 🔑 Authentication Flow

```
1. User tap "Continue with Google"
2. Firebase Google Sign-In → dapatkan ID Token
3. POST /auth/sync  { email } + Bearer Token
   ↳ is_new_user = true  → navigasi ke PersonalInfoScreen
   ↳ is_new_user = false → navigasi ke MainShellPage (home)
4. Untuk semua request selanjutnya, sertakan ID Token di header:
   Authorization: Bearer <firebase_id_token>
```

## ⚠️ Error Codes

| Status | Kode | Deskripsi |
|--------|------|-----------|
| 401 | Unauthorized | Token tidak ada atau tidak valid |
| 404 | Not Found | Resource tidak ditemukan |
| 422 | Unprocessable Entity | Validasi request body gagal |
| 500 | Internal Server Error | Error server |

---

*Last updated: 2026-05-23*
