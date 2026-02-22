import numpy, threading, moderngl, time
import data_ingester_

class error_corrector():
	"""I think that errors are due to mismatches in setp index and the actual data sets.
	I think this happens more when the measurement process's data transfer delay is low because it can do multiple transfers over the course of one ingestion on the plotting process's side.
	Meaning the data ingester reads the datasets, then reads the setp index of a future dataset."""
	def __init__(self, frequency : int, ssbo : moderngl.Buffer, data_ingester : data_ingester_.data_ingester):
		"""frequency in seconds that it checks for errors\n
		the ssbo to read from"""

		self.frequency = frequency
		self.ssbo = ssbo
		self.data_ingester = data_ingester
		self._running = False
		self._correction_thread = threading.Thread(target=self.correction_thread_target)
		self._ssbo_bytes = None
		self._formatted_dset = None
		self.requesting = False
		self.indexes_to_be_fixed = []
		
	def check_for_request(self, formatted_dset : numpy.ndarray):
		if self.requesting:
			if len(self.indexes_to_be_fixed):
				self.fix_errors(self.indexes_to_be_fixed)
				self.indexes_to_be_fixed.clear()
			self.fulfill_request(formatted_dset)
			#print("fulfilled request")

	def fulfill_request(self, formatted_dset : numpy.ndarray):
		self._ssbo_bytes = self.ssbo.read()
		self._formatted_dset = formatted_dset
		self.requesting = False

	def start_correction(self):
		self._running = True
		self._correction_thread.start()

	def stop_correction(self):
		self._running = False
		self._correction_thread.join()
		#print("thread ended")

	def correction_thread_target(self):
		while self._running:
			time.sleep(self.frequency)
			self.check_for_errors()

	def request(self):
		self.requesting = True
		while self.requesting:
			time.sleep(0.01)

	def read_ssbo(self) -> numpy.ndarray:
		dset = numpy.frombuffer(self._ssbo_bytes, dtype=numpy.float32)
		dset = dset.reshape(-1, 2)
		return dset
	
	def check_for_errors(self):
		self.request()
		dset = self.read_ssbo()

		nan_indexes = []
		nan_points = []
		for i in range(self.data_ingester.setp_index):
			#time.sleep(0.01)
			data_point = dset[i]
			if numpy.isnan(data_point[1]):
				nan_indexes.append(i)
				nan_points.append(data_point)
		self.indexes_to_be_fixed.extend(nan_indexes)
		#print(f"FOUND {len(nan_indexes)} errors")
		return (nan_indexes, nan_points)
	
	def fix_errors(self, error_indexes):
		#print(f"fixed {len(error_indexes)} errors")
		for index in error_indexes:
			self.ssbo.write(self._formatted_dset[index], offset=(index*4*2))