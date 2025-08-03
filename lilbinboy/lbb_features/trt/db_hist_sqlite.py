import logging
import timecode
from PySide6 import QtCore, QtSql, QtGui

class SnapshotDatabaseManager(QtCore.QObject):

	def __init__(self, database:QtSql.QSqlDatabase):

		self._db = database

		self.initializeDatabase()
	
	def initializeDatabase(self):
		"""Setup the initial database"""

		if not QtSql.QSqlQuery(self._db).exec("PRAGMA foreign_keys = ON;"):
			logging.getLogger(__name__).error("Error enabling foregin keys: %s", self._db.lastError().text())

		if not QtSql.QSqlQuery(self._db).exec(
			"""
			CREATE TABLE IF NOT EXISTS "trt_snapshot_labels" (
				"id_snapshot"	INTEGER NOT NULL UNIQUE,
				"label_name"	TEXT NOT NULL,
				"datetime_created"	TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
				"label_color"	TEXT,
				"rate"	INTEGER NOT NULL DEFAULT 24,
				"duration_trimmed_frames"	INTEGER NOT NULL DEFAULT 0,
				"duration_trimmed_tc"	TEXT NOT NULL DEFAULT '00:00:00:00',
				"duration_trimmed_ff"	TEXT NOT NULL DEFAULT '0+00',
				"duration_offset_frames"	INTEGER NOT NULL DEFAULT 0,
				"is_current"	INTEGER NOT NULL DEFAULT 0,
				PRIMARY KEY("id_snapshot" AUTOINCREMENT)
			)
			"""
		):
			logging.getLogger(__name__).error("Error setting up snapshot labels: %s", self._db.lastError().text())

		if not QtSql.QSqlQuery(self._db).exec(
			"""
			CREATE TABLE IF NOT EXISTS "trt_snapshot_sequences" (
				"id_snapshot"	INTEGER NOT NULL,
				"id_sequence"	INTEGER NOT NULL UNIQUE,
				"sequence_color"	TEXT,
				"sequence_name"	TEXT NOT NULL,
				"duration_trimmed_frames"	INTEGER NOT NULL,
				"duration_trimmed_tc"	TEXT NOT NULL,
				"duration_trimmed_ff"	TEXT NOT NULL,
				"datetime_created"	TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
				PRIMARY KEY("id_sequence" AUTOINCREMENT),
				FOREIGN KEY("id_snapshot") REFERENCES "trt_snapshot_labels"("id_snapshot") ON DELETE CASCADE
			)
			"""
		):
			logging.getLogger(__name__).error("Error setting up snapshot sequences: %s", self._db.lastError().text())
	
	def getSnapshotRecords(self, records:list[QtSql.QSqlRecord]):

		snapshot_ids = [record.field("id_snapshot").value() for record in records]

		query = QtSql.QSqlQuery(self._db)

		query_placeholders = ",".join(["?"]*len(snapshot_ids))
		query.prepare(
			f"""
			SELECT
				"id_snapshot",
				"sequence_color",
				"sequence_name",
				"duration_trimmed_tc",
				"duration_trimmed_ff",
				"duration_trimmed_frames"
			FROM trt_snapshot_sequences
			WHERE id_snapshot IN ({query_placeholders})
			"""
		)
		for place, snapshot_id in enumerate(snapshot_ids):
			query.bindValue(place, snapshot_id)
		query.exec()
		return query
	
	def getModelQuery(self):
		return QtSql.QSqlQuery(
			"""
			SELECT
				"id_snapshot",
				"label_name",
				"label_color",
				"rate",
				"duration_trimmed_frames",
				"duration_trimmed_tc",
				"duration_trimmed_ff",
				"duration_offset_frames",
				"is_current",
				datetime(datetime_created, "localtime") as "datetime_created_local"
			FROM trt_snapshot_labels
			ORDER BY is_current DESC, datetime_created DESC
			""",
			self._db)

	def saveLiveToSnapshot(self,
		snapshot_name:str,
		clip_color:QtGui.QColor,
		rate:int,
		adjust_frames:int,
		duration_frames:int, 
		timeline_info_list:list
	) -> int:

		query = QtSql.QSqlQuery(self._db)

		if clip_color.isValid():
			clip_color_str = ",".join(str(x) for x in [
				clip_color.red(),
				clip_color.green(),
				clip_color.blue()
			])
		else:
			clip_color_str = None

		# Copy "Current" snapshot label to new label
		query.prepare(
			"""
			INSERT INTO trt_snapshot_labels (
				"label_name",
				"label_color",
				"rate",
				"duration_trimmed_frames",
				"duration_trimmed_tc",
				"duration_trimmed_ff",
				"duration_offset_frames",
				"is_current"
			)

			VALUES (
				?,
				?,
				?,
				?,
				?,
				?,
				?,
				0
			)
			"""
		)
		query.addBindValue(snapshot_name)
		query.addBindValue(clip_color_str)
		query.addBindValue(rate)
		query.addBindValue(duration_frames)
		query.addBindValue(str(timecode.Timecode(duration_frames, rate=rate)))
		query.addBindValue(str(duration_frames)) # TODO: F+F
		query.addBindValue(adjust_frames)
		if not query.exec():
			logging.getLogger(__name__).error("Error creating snapshot group: %s", query.lastError().text())
		
		id_snapsphot_new = query.lastInsertId()
		
		# Copy sequences
		for timeline_info in timeline_info_list:
			query.prepare(
				"""
				INSERT INTO trt_snapshot_sequences(
					"id_snapshot",
					"sequence_color",
					"sequence_name",
					"duration_trimmed_frames",
					"duration_trimmed_tc",
					"duration_trimmed_ff"
				) VALUES (
					?,?,?,?,?,?
				)
				""")
			query.addBindValue(id_snapsphot_new)
			query.addBindValue(timeline_info.clip_color)
			query.addBindValue(timeline_info.name)
			query.addBindValue(timeline_info.duration_frames)
			query.addBindValue(timeline_info.duration_tc)
			query.addBindValue(timeline_info.duration_ff)

			if not query.exec():
				logging.getLogger(__name__).error("Error adding sequence to snapshot group: %s", query.lastError().text())

		return id_snapsphot_new
	
	def deleteSnapshotRecords(self, records:QtSql.QSqlRecord):

		id_snapshots = [record.field("id_snapshot").value() for record in records]
		query = QtSql.QSqlQuery(self._db)

		# Build placeholders
		placeholders = ",".join(["?"] * len(id_snapshots))

		query.prepare(
			f"""
			DELETE FROM trt_snapshot_labels
			WHERE id_snapshot IN ({placeholders})
			"""
		)
		for id_snapshot in id_snapshots:
			query.addBindValue(id_snapshot)
		
		if not query.exec():
			logging.getLogger(__name__).error("Error deleting snapshot group: %s", query.lastError().text())