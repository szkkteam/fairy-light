#!/bin/bash

LOCAL_WEBHOOK_DEBUG="$(stripe listen --events payment_intent.created,payment_intent.completed,charge.succeeded,charge.failed,payment_intent.payment_failed --log-level=debug)"
FORWARD_WEBHOOK_DEBUG="$(stripe listen --events payment_intent.created,payment_intent.completed,charge.succeeded,charge.failed,payment_intent.payment_failed --forward-to localhost:5000/shop/checkout-webhook --log-level=debug)"

# Run the selected command


case "$1" in

"local")
  echo "Executing: LOCAL_WEBHOOK_DEBUG"
  echo "$(LOCAL_WEBHOOK_DEBUG)"
  ;;
"forward")
  echo "Executing: FORWARD_WEBHOOK_DEBUG"
  echo "$(FORWARD_WEBHOOK_DEBUG)"
  ;;
*)
  echo "Executing: FORWARD_WEBHOOK_DEBUG"
  echo "$(FORWARD_WEBHOOK_DEBUG)"
  ;;

esac