import cv2

#创建对象
cap = cv2.VideoCapture(0)

#循环捕获视频
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame',gray)
    if cv2.waitKey(10) & 0xFF == 27:
    	break

# 停止捕获，释放对象
cap.release()
cv2.destroyAllWindows()
