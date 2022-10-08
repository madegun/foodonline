import datetime

def generate_order_no(pk):
  current_datetime = datetime.datetime.now().strftime('%d%m%Y%H%M') #convert format haribulantahunjammenit
  order_no = 'INV-'+ current_datetime + str(pk)
  return order_no
