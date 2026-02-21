[![ClawdTalk](https://clawdtalk.com/logo.svg)ClawdTalk\\
\\
Powered by ![Telnyx](https://clawdtalk.com/telnyx-wordmark.png)](https://clawdtalk.com/#)

[How it Works](https://clawdtalk.com/#how-it-works) [Features](https://clawdtalk.com/#features) [Pricing](https://clawdtalk.com/#pricing) [Live Demo](https://clawdtalk.com/#demo-video) [Contact Us](https://clawdtalk.com/#contact) [Log In](https://clawdtalk.com/login.html) [Sign Up](https://clawdtalk.com/signup.html)

[Log In](https://clawdtalk.com/login.html) [Sign Up](https://clawdtalk.com/signup.html)

Your Texts→Dialogs→VoiceTalk

# Give Your Clawdbot  a Voice.

Your bot handles text. We handle voice. Install the skill, verify your number, and call your Clawdbot like a phone call. It hears you speak, reads the transcript, and replies. You change nothing.

[Connect your Clawdbot (OpenClaw)](https://clawdtalk.com/signup.html) [Watch It Work ▶](https://clawdtalk.com/#how-it-works)

Call [301-MY-CLAWD](tel:+13016925293)

Incoming call fromClawdTalk

⌨Keypad

🎤Mute

🔊Speaker

⋯More

00:11

transcript

"Hey, can you check my calendar for tomorrow?"

Why Voice?

## Same task. Different world.

Drag the slider.

Without ClawdTalk

9:4117%

24Telegram

13Slack

8WhatsApp

5Messages

31Discord

47Mail

Slack#deploys: Health check failed on prod-3a9f

TelegramBot: Reminder - deploy review at 3pm

Discord@you mentioned in #general...

128 unread across 6 apps

With ClawdTalk

📞

ClawdTalk00:12

"Roll back prod to the last stable release and notify the team."


✓Rolled back. Team notified.

One call. Done.

◀▶

## How it works

Four boxes. That's the whole architecture.

![How ClawdTalk works - bidirectional voice and text flow](https://clawdtalk.com/how-it-works.gif)

#### What your bot receives:

```
{
  "event": "message",
  "call_id": "clk_7xK9mP",
  "text": "Hey, can you check my calendar for tomorrow?",
  "timestamp": "2025-02-01T19:58:00Z",
  "sequence": 1,
  "is_interruption": false
}
```

#### What your bot sends back:

```
{
  "type": "response",
  "call_id": "clk_7xK9mP",
  "text": "You have 3 meetings tomorrow."
}
```

## What you get

No PhD in telephony required.

📞

### Two-Way Calling

Call your bot from your phone. Or tell your bot "call me" and it does. Both directions work out of the box.

`POST /v1/calls { "to": "+15550123456456" }`

🔐

### PIN Protection

Set a PIN. Anyone calling without it gets rejected. Your bot. Your access control. Optional but recommended for shared numbers.

`pin: "8472" | attempts: 3 | bcrypt hashed`

🎙️

### Natural Sounding Voices

Premier speech-to-text and natural-sounding text-to-speech. Telnyx voices sound human, not robotic. Crystal clear communication.

`voice: "walnut", model: NaturalHD, latency: <200ms`

🔗

### WebSocket Connection

Your bot stays private with a persistent outbound WebSocket connection. No need for a publicly exposed gateway. Works behind NAT, firewalls, anywhere.

`./scripts/connect.sh start`

🌐

### Internet-First Global Network

Powered by Telnyx's full-stack infrastructure. Private fiber, direct carrier connections, global reach. When your bot talks, the world listens.

`latency: <100ms | uptime: 99.999%`

🔊

### HD Voice

Mobile networks support HD Voice. Your calls to your bot are crystal clear. No compression artifacts, no robot sound.

`codec: "AMR-WB", bitrate: "16kbps", quality: "wideband"`

Use Cases

## Talk to your bot like a person.

Because it already acts like one.

💻 Dev🏥 Health🛒 Shopping🏠 Home

ClawdTalk Call02:14

What's the status of the deploy pipeline?

The production deploy for commit 3a9f is running. Health check passed on 2 of 3 pods. One pod is stuck in CrashLoopBackOff.

Roll back to the last stable release.

Done. Rolled back to v2.4.1. All 3 pods healthy. I've posted a summary in the #deploys channel.

ClawdTalk Call01:32

Read me my Oura sleep score from last night.

You slept 7 hours 12 minutes. Sleep score 81. Deep sleep was low at 48 minutes. RHR was 52, which is normal for you.

Move my 3pm meeting to tomorrow same time.

Moved "Design Review" to tomorrow at 3pm. Attendees have been notified.

ClawdTalk Call01:47

Add oat milk and bananas to my grocery order.

Added to your Tesco basket. You also have eggs and sourdough from last time. Want me to book the next delivery slot?

Yeah, whatever's earliest.

Booked for tomorrow between 10am and noon. Total is £23.40.

ClawdTalk Call00:38

Turn off the living room lights and set the thermostat to 68.

Living room lights off. Thermostat set to 68°F. It's currently 72 inside, should reach target in about 20 minutes.

And lock the front door.

Front door locked. All secure.

## Call [301-MY-CLAWD](tel:+13016925293)

Instant connection to your bot.

Call [301-MY-CLAWD](tel:+13016925293)

M6Y9C2L5A2W9D3

We validate you by Caller ID + a PIN you establish during sign-up. It's enforced server-side, so no tricking your bot. Upgrade to get your own dedicated number.

By texting CLAWD to 25293 you consent to receive 2FA, Conversational and Alerts text messages. Text STOP to opt out and HELP for support or reach out to support@telnyx.com. Message frequency may vary. Message and data rates may apply. [Privacy Policy](https://support.telnyx.com/en/articles/4557103-telnyx-privacy-policy). [Terms](https://telnyx.com/terms-and-conditions-of-service).

## Choose Your Plan

Free means free. No credit card. No "trial expires in 14 days."

Monthly
Annual
Save up to 30%

Free

$0/forever

Perfect for testing and small projects

10 call minutes/month

100 texts/month

Full transcripts

Community support

No recordings

No phone numbers

Missions (Coming Soon)

[Get Started](https://clawdtalk.com/signup.html)

Most Popular

Starter

$12/month

Save $44/yr

For individuals and small teams

\+ $20 setup fee for number registration

Order your own number

100 call minutes/month

100 texts/month

Missions (Coming Soon)

Full transcripts

Call recordings (Coming Soon)

AI support

No overages

No summaries

[Upgrade to Starter](https://clawdtalk.com/signup.html)

Pro

$30/month

Save $110/yr

For businesses that need more

\+ $20 setup fee for number registration

Order your own number

500 call minutes/month

500 texts/month

Missions (Coming Soon)

Full transcripts & recordings

Summaries (Coming Soon)

Human support

Overages allowed

Overage rates:

Calls: $0.02/min overage

Texts: $0.01/message overage

Missions: Coming Soon

[Upgrade to Pro](https://clawdtalk.com/signup.html)

## See it in action

A real call between a developer and their Clawdbot. Voices by Telnyx NaturalHD.

Your browser does not support the video tag.


FAQ

## Questions? Answered.

The stuff you're probably wondering.

How is this different from Twilio?

Twilio gives you telephony primitives. You still need to spin up a WebSocket server, pipe raw audio to a speech-to-text service, route text to your bot, send the response to a text-to-speech service, and stream audio back. That's 3-4 services and a publicly deployed server just to say "hello." ClawdTalk skips all of that. Your bot receives text, returns text. We handle the number, the audio, the transcription, and the synthesis.

Will this expose my bot to the public internet?

No. ClawdTalk uses a persistent outbound WebSocket connection. Your bot connects to us - we never connect to you. It works behind NAT, firewalls, VPNs, Docker networks - anywhere that can make an outbound HTTPS connection. No port forwarding, no public IP, no exposed endpoints. Your bot stays exactly where it is.

What's the latency like?

ClawdTalk uses Telnyx AI Assistants for the real-time voice loop — purpose-built for sub-200ms conversational latency. The voice agent handles the call independently, so you get instant responses. When the AI Assistant needs to reach your Clawdbot (for memory, tools, or complex tasks), it uses async tool calls — your bot processes in the background while the voice agent keeps the conversation flowing naturally. This separation means the voice experience stays snappy even when your bot is doing heavy lifting.

Is my data private?

Your bot runs on your hardware. ClawdTalk only sees the text during a call. No training on your data. No logs stored beyond what you configure.

Can my bot make outbound calls?

On the free tier, your bot can only call your verified number. This restriction exists to prevent fraud and abuse. On the Pro plan, you get a dedicated number assigned to your bot and can make outbound calls to any number.

What does "free tier" actually mean?

Free means free. No credit card. No trial that expires in 14 days. You get a real phone number and real minutes. When you need more, you pay per month.

Get in Touch

## Contact Us

Questions about ClawdTalk, pricing, or integrations? Drop us a line.

First name \*

Last name \*

Business email \*

Company

Phone number

How can we help? \*

I agree to receive communications from Telnyx about ClawdTalk, including by email, phone, and text message. I understand I can unsubscribe at any time. By submitting this form, I acknowledge the [Privacy Policy](https://telnyx.com/privacy-policy) and [Terms of Service](https://telnyx.com/terms-and-conditions-of-service).

Send Message

✓ Thanks! We'll be in touch soon.


Something went wrong. Please try again or email us directly.


## Stop typing.  Start talking.

Your ClawdBot is one phone call away.

[Connect your Clawdbot (OpenClaw)](https://clawdtalk.com/signup.html)

Or call now: [301-MY-CLAWD](tel:+13016925293)

Powered by![Telnyx](https://clawdtalk.com/telnyx-wordmark.png)

![ClawdTalk logo](https://clawdtalk.com/logo.svg)**ClawdTalk**

Give your Clawdbot a voice. Zero friction.

Powered by![Telnyx](https://clawdtalk.com/telnyx-wordmark.png)

#### Product

[How it Works](https://clawdtalk.com/#how-it-works) [Features](https://clawdtalk.com/#features) [Pricing](https://clawdtalk.com/#pricing) [Live Demo](https://clawdtalk.com/#demo-video) [Log In](https://clawdtalk.com/login.html) [Sign Up](https://clawdtalk.com/signup.html)

#### Resources

[OpenClaw Docs](https://docs.openclaw.ai/) [Discord](https://discord.gg/HdHaam4RAh)

#### Company

[Telnyx.com](https://telnyx.com/) [Telnyx Pricing](https://telnyx.com/pricing) [Contact](https://telnyx.com/contact-us)

#### Legal

[Privacy Policy](https://clawdtalk.com/privacy.html) [Terms of Service](https://clawdtalk.com/terms.html)

Powered by![Telnyx](https://clawdtalk.com/telnyx-wordmark.png)

© 2026 Telnyx. All rights reserved.