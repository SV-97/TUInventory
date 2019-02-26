    def find_and_mark_barcodes(self, frame):
        """Find barcodes in given frame
            Args:
                frame: Frame that barcodes are to be detected in
            Returns: 
                Tuple of frame where barcodes are marked, list of all found codes in frame
        """
        barcodes = pyzbar.decode(frame)
        found_codes = []
        for barcode in barcodes:
            barcode_information = (barcode.type, barcode.data.decode("utf-8"))
            if barcode_information not in found_codes:
                found_codes.append(barcode_information)
            poly = barcode.polygon
            poly = np.asarray([(point.x, point.y) for point in poly])
            poly = poly.reshape((-1, 1, 2))
            cv2.polylines(frame, [poly], True, (0, 255, 0), 2)
            cv2.rectangle(frame, *self.rect_transformation(*barcode.rect), (255, 0, 0), 2)
            x, y = barcode.rect[:2]
            cv2.putText(
                frame, 
                "{}({})".format(*barcode_information), 
                (x, y - 10), 
                cv2.FONT_HERSHEY_PLAIN, 
                1, 
                (0, 0, 255), 
                1)
        return frame, found_codes