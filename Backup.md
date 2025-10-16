# Forest Fire Backup Procedure

This document details the steps to perform incremental backups of the **media folder** and **database snapshots** from the remote server to a local machine.

---

## Step 1 – Incremental Backup of Media Folder

**Command:**

```bash
rsync -avz root@139.162.11.234:/root/Forest-Fire-Detection/media/ /path/to/Forest_Fire_Backup/media/
```

**Purpose:** Perform an **incremental backup** of the media folder, copying only new or modified files from the remote server to the local machine.

**Flags:**

- `-a` (archive): Preserves permissions, ownership, timestamps, symbolic links, and recursively copies directories.
- `-v` (verbose): Shows detailed progress.
- `-z` (compress): Compresses data during transfer to save bandwidth.

**Source and Destination:**

- **Source (remote):** `root@139.162.11.234:/root/Forest-Fire-Detection/media/`
  > The trailing `/` ensures only the folder contents are copied.
- **Destination (local):** `/path/to/Forest_Fire_Backup/media/`

---

## Step 2 – Copy Database Backup File

**Command:**

```bash
scp root@139.162.11.234:/root/backup_forest_fire_20251015.sql /path/to/Forest_Fire_Backup/dbs_snapshots/
```

**Purpose:** Securely copy a **single database backup file** from the remote server to the local machine.

**Notes:**

- File names follow the **YYYYMMDD** format.
- You can download the **latest 5 trailing days** of snapshots from the server.

---

## Logic

- Each SQL file can be used to locate **events and associated media files**.
- The database changes over time, but the **media folder** remains consistent for serving files.

---

## Daily Backup Workflow

| Step | Task                     | Command                                                                                                    | Destination                                  |
| ---- | ------------------------ | ---------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| 1    | Backup media folder      | `rsync -avz root@139.162.11.234:/root/Forest-Fire-Detection/media/ /path/to/Forest_Fire_Backup/media/`     | `/path/to/Forest_Fire_Backup/media/`         |
| 2    | Backup database snapshot | `scp root@139.162.11.234:/root/backup_forest_fire_YYYYMMDD.sql /path/to/Forest_Fire_Backup/dbs_snapshots/` | `/path/to/Forest_Fire_Backup/dbs_snapshots/` |

> **Tip:** Replace `YYYYMMDD` with the date of the snapshot you wish to download.

---

## Additional Notes

1. **Adaptable for the other project as well:**

   - You can replace the folder name `Forest-Fire-Detection` to `wwf-snow-leopard` while keeping the same directory structure.
   - Both of the projects and servers follow same layout for this purpose.

2. **Automation:**

   - These commands can be added to a **cron job** to automate daily incremental backups.

3. **Managing Large Backups:**

   - After accumulating a large number of incremental backups, consider transferring them to the **SSD or cloud storage**.
   - Start a new backup directory periodically (e.g., every few months) to avoid filling a single directory.


