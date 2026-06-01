#!/usr/bin/env python3
"""Generate adaptive Screen 3 flow data for index.html integration."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

S2 = {
    "service": ["IT & TECH","CONSULTING","LEGAL","ACCOUNTING","MARKETING","HEALTHCARE","STAFFING","CLEANING","SECURITY","HOSPITALITY","FOOD SERVICE","CREATIVE"],
    "manufacturing": ["FOOD & BEV","ELECTRONICS","TEXTILES","CHEMICALS","METAL & STEEL","AUTOMOTIVE","FURNITURE","MEDICAL","CONSTRUCTION","PLASTICS","PRINT & PAPER","AGRI-PROC"],
    "agriculture": ["CROP FARMING","LIVESTOCK","DAIRY","POULTRY","AQUACULTURE","HORTICULTURE","ORGANIC","PROCESSING","PLANTATION","SEED SUPPLY","IRRIGATION","EXPORT/TRADE"],
    "logistics": ["ROAD/TRUCKING","AIR FREIGHT","SEA/OCEAN","RAIL","WAREHOUSING","LAST MILE","COLD CHAIN","CUSTOMS","SUPPLY CHAIN","MOVING","E-COMM FULFIL","FREIGHT FWDG"],
    "finance": ["BANKING","INSURANCE","INVESTMENT","ACCOUNTING","FINTECH","LENDING","WEALTH MGMT","PAYMENTS","CRYPTO","RISK","TRADING","MICROFINANCE"],
    "construction": ["RESIDENTIAL","COMMERCIAL","INFRASTRUCTURE","ELECTRICAL","PLUMBING","INTERIOR","RENOVATION","DEMOLITION","REAL ESTATE","CIVIL ENG","ENVIRONMENTAL","FUEL/ENERGY"],
    "retail": ["APPAREL","ELECTRONICS","GROCERY","HARDWARE","PHARMACY","FURNITURE","JEWELRY","SPORTING","E-COMMERCE","AUTO PARTS","BOOKS/STAT","HOME DECOR"],
    "education": ["K-12","HIGHER ED","VOCATIONAL","ED-TECH","CORP TRAINING","TUTORING","LANGUAGE","TEST PREP","ARTS & MUSIC","SPORTS","EARLY CHILD","SPECIAL ED"],
    "entertainment": ["MUSIC","FILM & VIDEO","GAMING","LIVE EVENTS","STREAMING","SOCIAL MEDIA","PUBLISHING","PHOTOGRAPHY","ANIMATION","THEATRE","SPORTS MEDIA","ADVERTISING"],
}

CAT_LABEL = {
    "service": "service business",
    "manufacturing": "manufacturing operation",
    "agriculture": "agriculture operation",
    "logistics": "logistics operation",
    "finance": "financial services firm",
    "construction": "construction business",
    "retail": "retail operation",
    "education": "education provider",
    "entertainment": "entertainment business",
}

# Hand-curated subtype context (client/unit/work verbs)
SUBTYPE_CTX = {
    ("service","IT & TECH"): {"client":"prospect","unit":"a software build or IT support scope","work":"project","deliver":"ship the build"},
    ("service","CONSULTING"): {"client":"prospect","unit":"an advisory engagement","work":"engagement","deliver":"deliver recommendations"},
    ("service","LEGAL"): {"client":"potential client","unit":"a legal matter","work":"case","deliver":"close the matter"},
    ("service","HEALTHCARE"): {"client":"patient","unit":"a care appointment or treatment plan","work":"care plan","deliver":"deliver care"},
    ("service","MARKETING"): {"client":"brand client","unit":"a campaign scope","work":"campaign","deliver":"launch the campaign"},
    ("service","ACCOUNTING"): {"client":"client","unit":"a tax or bookkeeping scope","work":"engagement","deliver":"close the books"},
    ("logistics","COLD CHAIN"): {"client":"shipper","unit":"a temperature-sensitive shipment","work":"load","deliver":"deliver in-spec"},
    ("logistics","LAST MILE"): {"client":"customer","unit":"a same-day delivery","work":"route","deliver":"complete delivery"},
    ("logistics","WAREHOUSING"): {"client":"client","unit":"an inbound inventory batch","work":"fulfillment wave","deliver":"ship orders"},
    ("logistics","CUSTOMS"): {"client":"importer","unit":"a customs clearance file","work":"clearance","deliver":"release shipment"},
    ("manufacturing","FOOD & BEV"): {"client":"buyer","unit":"a production batch","work":"batch","deliver":"release batch"},
    ("manufacturing","ELECTRONICS"): {"client":"buyer","unit":"a production run","work":"run","deliver":"ship units"},
    ("agriculture","CROP FARMING"): {"client":"buyer","unit":"a harvest lot","work":"season","deliver":"move the crop"},
    ("agriculture","DAIRY"): {"client":"buyer","unit":"a daily milk collection","work":"collection","deliver":"deliver milk"},
    ("construction","RESIDENTIAL"): {"client":"homeowner","unit":"a home build or remodel","work":"job","deliver":"hand over keys"},
    ("construction","COMMERCIAL"): {"client":"developer","unit":"a commercial build","work":"project","deliver":"substantial completion"},
    ("retail","E-COMMERCE"): {"client":"shopper","unit":"an online order","work":"order","deliver":"fulfill the order"},
    ("retail","GROCERY"): {"client":"shopper","unit":"a basket of goods","work":"transaction","deliver":"complete checkout"},
    ("finance","FINTECH"): {"client":"user","unit":"an onboarding flow","work":"account","deliver":"activate the account"},
    ("finance","LENDING"): {"client":"borrower","unit":"a loan application","work":"loan","deliver":"fund the loan"},
    ("education","ED-TECH"): {"client":"learner","unit":"a course enrollment","work":"cohort","deliver":"complete the module"},
    ("education","K-12"): {"client":"student","unit":"a term enrollment","work":"term","deliver":"report progress"},
    ("entertainment","GAMING"): {"client":"player","unit":"a game release cycle","work":"release","deliver":"ship the build"},
    ("entertainment","FILM & VIDEO"): {"client":"client","unit":"a production schedule","work":"production","deliver":"deliver the cut"},
}

def slug(name: str) -> str:
    s = name.lower().replace("/", "-").replace("&", "").strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")

def default_ctx(category: str, subtype: str) -> dict:
    st = subtype.lower()
    return {
        "subtype": subtype,
        "category": CAT_LABEL[category],
        "client": "customer" if category in ("retail", "logistics") else "client",
        "unit": f"a typical {st} job",
        "work": "job",
        "deliver": "complete the job",
    }

def merge_ctx(category: str, subtype: str) -> dict:
    base = default_ctx(category, subtype)
    base.update(SUBTYPE_CTX.get((category, subtype), {}))
    base["title"] = f"YOUR {subtype} OPERATION, STAGE BY STAGE"
    return base

# Category flow templates: each stage uses {placeholders}
FLOWS = {
"service": {
  "stages": [
    {"name":"Get Leads","icon":"lead","q":"A new {client} inquiry comes in for {unit}. How is it captured?",
     "opts":["Logged in one system with source tracked.","We take the details but tracking is inconsistent.","It lands in inbox, texts, and memory — nothing unified."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Leads arrive but aren't logged consistently — follow-ups slip and forecasting breaks.","missing":"Demand looks random because intake isn't tracked anywhere reliable."},
     "fix":"Lead capture + CRM"},
    {"name":"Scope","icon":"qualify","q":"Before quoting {unit}, how do you define scope?",
     "opts":["Structured discovery before any quote goes out.","A few questions, then we estimate from experience.","We start work and figure scope out as we go."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Gut-feel scoping under-prices hard {work}s and quietly erodes margin.","missing":"Scope creep shows up mid-{work} and you absorb the overrun."},
     "fix":"Scoping framework"},
    {"name":"Proposal","icon":"quote","q":"A hot {client} asks for pricing on {unit}. How fast do they get a proposal?",
     "opts":["Same day from a proven template.","A day or two while we build it manually.","Whenever we get to it — could be next week."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Manual proposals slow you down — faster competitors win while you're drafting.","missing":"Delayed proposals kill momentum before the {work} even starts."},
     "fix":"Proposal templates + e-sign"},
    {"name":"Deliver","icon":"build","q":"Two active {work}s are running. Where does status live?",
     "opts":["One tool — anyone can see progress.","Mostly Slack threads and one person's head.","We hear about slips when the {client} calls."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Status lives in messages and memory — deadlines collide without warning.","missing":"No single view of delivery means surprises become client escalations."},
     "fix":"Delivery tracking + PM"},
    {"name":"Get Paid","icon":"invoice","q":"A {work} finished two weeks ago. What's happening with billing?",
     "opts":["Invoice sent with automated reminders.","I'll invoice soon when I remember.","Wait — did we bill that one?"],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Billing follows memory, not milestones — cash comes in late.","missing":"Unbilled work and missed invoices make cash flow unpredictable."},
     "fix":"Milestone billing + reminders"},
    {"name":"Retain","icon":"retain","q":"Three months after you {deliver}, what's the {client} relationship?",
     "opts":["On a retainer or scheduled check-ins.","I reach out when I remember.","The {work} ended, so the relationship ended."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Ad-hoc check-ins let clients drift to whoever stayed visible.","missing":"Every {work} is a reset — you rebuild pipeline from zero."},
     "fix":"Retainer + check-in cadence"},
  ]
},
"manufacturing": {
  "stages": [
    {"name":"Demand","icon":"lead","q":"A new order for {unit} comes in. How do you intake demand?",
     "opts":["ERP/CRM captures every order with lead time.","Spreadsheets and email — mostly works.","Orders arrive by phone and paper — hard to consolidate."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Demand sits in silos — production plans react late to changes.","missing":"Without unified intake you over-promise or under-utilize capacity."},
     "fix":"Order intake + ERP sync"},
    {"name":"Plan","icon":"qualify","q":"Before the line runs {unit}, how is production planned?",
     "opts":["MRP/scheduling tool drives the plan.","Supervisor plans from experience each morning.","We run what feels urgent — no formal plan."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Manual planning causes changeovers and stockouts you didn't see coming.","missing":"Reactive planning burns overtime and misses delivery dates."},
     "fix":"Production scheduling system"},
    {"name":"Quality","icon":"quote","q":"Mid-{work}, a quality issue appears. How is it handled?",
     "opts":["Logged, traced, and corrected in-process.","We fix it but records are patchy.","We find out from the customer or audit."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Quality fixes happen but traceability gaps risk recalls and rework.","missing":"Late quality discovery means scrap, returns, and reputation damage."},
     "fix":"QMS + batch traceability"},
    {"name":"Ship","icon":"build","q":"Finished {unit} is ready. How do you fulfill and ship?",
     "opts":["WMS tracks pick, pack, and shipment status.","Warehouse team coordinates over radio/chat.","Shipments go out when someone remembers to book freight."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Fulfillment coordination by chat creates mispicks and late trucks.","missing":"Shipping chaos creates chargebacks and lost customers."},
     "fix":"WMS + shipping integration"},
    {"name":"Invoice","icon":"invoice","q":"Goods shipped last week — where is the invoice?",
     "opts":["Auto-generated from shipment confirmation.","Finance sends it after manual reconciliation.","Billing happens whenever someone gets to it."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Manual billing lags shipment — working capital gets tied up.","missing":"Missed invoices and wrong quantities hurt margin silently."},
     "fix":"Ship-to-invoice automation"},
    {"name":"Account Mgmt","icon":"retain","q":"Six months after delivery, how do you manage the buyer relationship?",
     "opts":["Account reviews and reorder forecasts on cadence.","We check in when they reorder.","No structured follow-up — they call when they need more."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Reactive account management lets competitors capture repeat volume.","missing":"No account rhythm means demand feels lumpy and unpredictable."},
     "fix":"Account planning + reorder alerts"},
  ]
},
"logistics": {
  "stages": [
    {"name":"Win Load","icon":"lead","q":"A {client} offers {unit}. How do you capture and price it?",
     "opts":["TMS quotes, books, and logs the load instantly.","We quote in email then enter it later.","Loads get accepted on calls — nothing centralized."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Delayed load entry means dispatch finds out late — margins shrink.","missing":"Scattered booking creates double-bookings and missed loads."},
     "fix":"TMS + digital booking"},
    {"name":"Plan Route","icon":"qualify","q":"Before wheels roll on {unit}, how is the route planned?",
     "opts":["Routing software optimizes mode, time, and cost.","Dispatcher plans from experience.","Drivers figure out the best route themselves."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Manual routing burns fuel and misses time windows.","missing":"No route discipline means late deliveries and penalty fees."},
     "fix":"Route optimization"},
    {"name":"Track","icon":"build","q":"{unit} is in transit. Can you see status in real time?",
     "opts":["Live tracking with exception alerts.","Updates when the driver calls in.","We find out status when the {client} asks."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Check-call tracking hides delays until they're expensive to fix.","missing":"Blind spots in transit create disputes you can't defend."},
     "fix":"Real-time tracking + alerts"},
    {"name":"Deliver","icon":"quote","q":"At delivery of {unit}, how is proof captured?",
     "opts":["Digital POD with photos/signatures synced instantly.","Paper POD collected and entered later.","PODs get lost — billing waits on paperwork."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Late POD entry delays billing and triggers payment disputes.","missing":"Missing proof-of-delivery backs you into revenue write-offs."},
     "fix":"Digital POD workflow"},
    {"name":"Bill","icon":"invoice","q":"Delivery complete — when does the invoice go out?",
     "opts":["Auto-invoiced from POD + rate confirmation.","Billing batch runs weekly.","Invoices depend on someone remembering."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Batch billing stretches DSO and hides unbilled accessorials.","missing":"Ad-hoc invoicing leaves money on the table every month."},
     "fix":"Auto-rating + billing"},
    {"name":"Renew","icon":"retain","q":"After successful {work}s, how do you keep the {client}?",
     "opts":["Contract reviews and lane analytics on schedule.","We react when they tender new freight.","No account plan — they shop rates every time."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Reactive account handling makes you a commodity on every bid.","missing":"No retention motion means constant re-selling the same lanes."},
     "fix":"Account reviews + lane KPIs"},
  ]
},
"agriculture": {
  "stages": [
    {"name":"Market","icon":"lead","q":"A buyer wants {unit}. How do you track demand and pricing?",
     "opts":["CRM/market board with buyer history.","Notebook and phone calls.","We sell to whoever calls on harvest day."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Weak market tracking means you miss better prices by days.","missing":"Spot-only selling exposes you to volatile margins."},
     "fix":"Buyer CRM + price tracking"},
    {"name":"Plan Season","icon":"qualify","q":"Before the {work}, how do you plan inputs and labor?",
     "opts":["Season plan with costs and timing in one place.","Rough plan in spreadsheets.","We plan week-to-week as things come up."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Loose planning causes input shortages at the worst time.","missing":"No season plan means reactive spending and yield risk."},
     "fix":"Season planning tool"},
    {"name":"Operate","icon":"build","q":"During {work}, how do you monitor field/barn operations?",
     "opts":["Sensors/logs with daily operational dashboard.","Walk the operation and check manually.","Issues show up when damage is already done."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Manual monitoring misses early warning signs — yield takes the hit.","missing":"Late detection of issues turns small fixes into big losses."},
     "fix":"Ops monitoring + alerts"},
    {"name":"Sell","icon":"quote","q":"At harvest/sale time for {unit}, how do you manage fulfillment?",
     "opts":["Grading, packing, and shipment tracked end-to-end.","Mostly coordinated by phone on pickup day.","Buyers wait while we scramble to organize pickup."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Last-minute fulfillment coordination discounts your product.","missing":"Chaotic sell-side ops erodes trust with repeat buyers."},
     "fix":"Harvest logistics workflow"},
    {"name":"Collect","icon":"invoice","q":"Product delivered — how do you collect payment?",
     "opts":["Invoices/receipts tied to shipment with reminders.","We chase payments when cash gets tight.","Payments trail delivery by weeks with no system."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Manual collections stretch cash through the off-season.","missing":"Weak billing lets buyers stretch terms indefinitely."},
     "fix":"Invoice + collections cadence"},
    {"name":"Next Season","icon":"retain","q":"After the season, how do you prepare the next cycle?",
     "opts":["Post-season review with buyer and input plans locked.","We debrief informally and move on.","Each season starts from scratch with no review."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Informal reviews repeat the same mistakes next season.","missing":"No learning loop means margin leaks compound year over year."},
     "fix":"Season retrospective + planning"},
  ]
},
"finance": {
  "stages": [
    {"name":"Acquire","icon":"lead","q":"A new {client} shows interest in {unit}. How is the lead handled?",
     "opts":["CRM with source, fit score, and next step.","Advisor inbox and follow-up list.","Leads sit in email until someone has time."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Leads without structured follow-up go cold quietly.","missing":"Pipeline visibility is zero — growth feels random."},
     "fix":"CRM + lead routing"},
    {"name":"Qualify","icon":"qualify","q":"Before offering {unit}, how do you run KYC/fit checks?",
     "opts":["Standardized checklist with approvals logged.","We ask key questions but it's inconsistent.","We onboard first and fix compliance gaps later."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Inconsistent qualification creates rework and compliance risk.","missing":"Late KYC catches issues after time is already spent."},
     "fix":"KYC/qualification workflow"},
    {"name":"Propose","icon":"quote","q":"Qualified {client} needs a proposal for {unit}. How fast?",
     "opts":["Template-based proposal same day.","Custom deck built over several days.","Proposal timing depends on bandwidth."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Slow proposals lose to faster firms with similar offerings.","missing":"Inconsistent proposal quality hurts close rates."},
     "fix":"Proposal automation"},
    {"name":"Onboard","icon":"build","q":"{client} says yes — how does onboarding run?",
     "opts":["Guided onboarding with status visible to all.","Email docs back and forth until done.","Onboarding drags because steps aren't tracked."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Document ping-pong delays revenue start dates.","missing":"Broken onboarding creates early churn and compliance gaps."},
     "fix":"Onboarding portal"},
    {"name":"Serve","icon":"invoice","q":"Active {client} needs ongoing service on {unit}. How is it managed?",
     "opts":["Service calendar + case tracking in one system.","Handled ad hoc when they reach out.","We only hear issues when they're already upset."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Reactive service misses upsell and retention moments.","missing":"No service system means churn shows up too late."},
     "fix":"Client service hub"},
    {"name":"Retain","icon":"retain","q":"Annual review time — how do you retain the {client}?",
     "opts":["Review pack with performance data and next steps.","Informal catch-up when calendar allows.","No review — they decide silently whether to stay."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Informal reviews leave assets vulnerable to poaching.","missing":"Silent churn happens when no one owns the relationship."},
     "fix":"Review cadence + health score"},
  ]
},
"construction": {
  "stages": [
    {"name":"Find Bid","icon":"lead","q":"A {unit} opportunity appears. How do you track it?",
     "opts":["Bid board with deadlines and go/no-go logged.","Estimator folder and memory.","Jobs come through network — nothing tracked centrally."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Untracked bids mean missed deadlines and wrong pursuits.","missing":"No bid pipeline makes growth unpredictable."},
     "fix":"Bid tracking board"},
    {"name":"Estimate","icon":"qualify","q":"You pursue {unit}. How is the estimate built?",
     "opts":["Standard takeoff template with cost database.","Spreadsheet built from similar past jobs.","Field guess — refined after work starts."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Template-free estimating misses scope gaps that kill margin.","missing":"Guess-based bids win jobs you lose money on."},
     "fix":"Estimating system"},
    {"name":"Contract","icon":"quote","q":"You win {unit}. How fast is the contract executed?",
     "opts":["Contract pack sent for e-sign within 24 hours.","Legal review takes a week or more.","Work starts before paperwork is fully signed."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Slow contracting delays mobilization and cash flow.","missing":"Starting without signed scope creates dispute exposure."},
     "fix":"Contract templates + e-sign"},
    {"name":"Build","icon":"build","q":"On site for {unit}, how is progress tracked?",
     "opts":["Daily logs, photos, and schedule in one platform.","Foreman updates by text at end of day.","We learn about delays from the {client}."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Text-based updates hide schedule drift until it's costly.","missing":"No job visibility means RFIs and change orders pile up."},
     "fix":"Job site tracking"},
    {"name":"Bill","icon":"invoice","q":"Work complete on a milestone — when do you bill?",
     "opts":["Pay app submitted on milestone with backup docs.","Invoice when admin catches up.","Billing backlog builds until cash gets tight."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Late pay apps starve cash and weaken GC relationships.","missing":"Billing gaps on {work}s compound into serious cash crises."},
     "fix":"Progress billing workflow"},
    {"name":"Repeat","icon":"retain","q":"After you {deliver}, how do you win the next {unit}?",
     "opts":["Closeout package + maintenance pitch on schedule.","We call if we hear of another project.","No follow-up — hope they call us again."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Passive follow-up loses repeat work to proactive competitors.","missing":"No closeout motion means every job is a cold start."},
     "fix":"Closeout + referral system"},
  ]
},
"retail": {
  "stages": [
    {"name":"Traffic","icon":"lead","q":"Shoppers need to find your {unit}. How do you drive traffic?",
     "opts":["Tracked campaigns with daily traffic metrics.","Promotions when sales dip.","Foot traffic or clicks feel random."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Untracked promotions waste spend on the wrong channels.","missing":"Random traffic means you can't forecast inventory or staffing."},
     "fix":"Marketing analytics"},
    {"name":"Merchandise","icon":"qualify","q":"Before selling {unit}, how is inventory and display managed?",
     "opts":["POS-linked inventory with reorder alerts.","Stock counts done periodically.","We discover stockouts when customers ask."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Periodic counts miss shrink and stockouts between audits.","missing":"Blind inventory causes lost sales and angry customers."},
     "fix":"Inventory + replenishment"},
    {"name":"Sell","icon":"quote","q":"A {client} wants {unit}. How smooth is checkout?",
     "opts":["Fast checkout — online or in-store with one system.","Checkout works but promos/discounts are manual.","Lines build because systems don't talk."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Manual checkout steps slow peak hours and lose baskets.","missing":"Friction at checkout kills conversion you paid to acquire."},
     "fix":"Unified POS/checkout"},
    {"name":"Fulfill","icon":"build","q":"Order placed — how is {unit} fulfilled?",
     "opts":["Pick/pack/ship tracked with customer notifications.","Fulfillment handled but updates are manual.","Customers call asking where their order is."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Manual fulfillment updates drive WISMO calls and bad reviews.","missing":"Opaque fulfillment erodes repeat purchase rates."},
     "fix":"OMS + tracking notifications"},
    {"name":"Reconcile","icon":"invoice","q":"End of week — how do you reconcile sales and cash?",
     "opts":["Daily close with POS, payments, and bank matched.","Reconciled when accounting has time.","Discrepancies show up at month-end."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Delayed reconciliation hides leakage until it's large.","missing":"Late close means you operate blind to shrink and errors."},
     "fix":"Daily reconciliation"},
    {"name":"Loyalty","icon":"retain","q":"After purchase, how do you bring the {client} back?",
     "opts":["Loyalty/CRM with segmented follow-ups.","Occasional email blasts.","No retention program — hope they return."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Generic blasts underperform targeted retention by a wide margin.","missing":"No loyalty loop means you re-buy every customer from scratch."},
     "fix":"CRM + loyalty program"},
  ]
},
"education": {
  "stages": [
    {"name":"Enroll","icon":"lead","q":"A {client} wants to enroll in {unit}. How is intake handled?",
     "opts":["Enrollment funnel with status and follow-up automated.","Forms emailed back and forth.","Enrollment depends on phone tag."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Manual enrollment leaks prospects between inquiry and start date.","missing":"Phone-tag intake caps growth and frustrates families."},
     "fix":"Enrollment CRM"},
    {"name":"Assess","icon":"qualify","q":"Before teaching {unit}, how do you assess the {client}?",
     "opts":["Standard assessment with placement logged.","Informal conversation about level.","Everyone starts at the same point."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Weak placement causes churn when content misfits the learner.","missing":"No assessment means poor outcomes and refund pressure."},
     "fix":"Assessment workflow"},
    {"name":"Teach","icon":"build","q":"During {work}, how is delivery tracked?",
     "opts":["LMS/attendance with progress dashboards.","Instructor notes and memory.","We discover gaps when complaints arrive."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Instructor-only tracking hides at-risk learners until too late.","missing":"No delivery visibility drives dropout and bad reviews."},
     "fix":"LMS + progress tracking"},
    {"name":"Report","icon":"quote","q":"Mid-{work}, how do stakeholders see progress on {unit}?",
     "opts":["Automated progress reports on schedule.","Reports built manually before meetings.","Parents/clients ask because they haven't heard anything."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Manual reporting consumes instructor time and still arrives late.","missing":"Silence on progress erodes trust fast."},
     "fix":"Automated progress reports"},
    {"name":"Bill","icon":"invoice","q":"Fees for {unit} — how is billing handled?",
     "opts":["Recurring billing with reminders and receipts.","Invoices sent when someone remembers.","Payment follow-up is awkward and inconsistent."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Inconsistent billing creates awkward conversations and arrears.","missing":"Weak fee collection threatens cash and continuation."},
     "fix":"Tuition billing automation"},
    {"name":"Retain","icon":"retain","q":"Term ending — how do you retain the {client}?",
     "opts":["Renewal campaign with next-term plan ready.","We mention re-enrollment at pickup.","Students drift unless they proactively return."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Casual renewal mentions miss a big chunk of repeat enrollments.","missing":"No renewal system makes every term a rebuild."},
     "fix":"Renewal workflow"},
  ]
},
"entertainment": {
  "stages": [
    {"name":"Audience","icon":"lead","q":"You need audience for {unit}. How do you grow it?",
     "opts":["Analytics across channels with content calendar.","Post when something is ready.","Reach feels unpredictable."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Inconsistent publishing wastes momentum between releases.","missing":"Random reach makes every launch start from zero."},
     "fix":"Audience analytics + calendar"},
    {"name":"Pitch","icon":"qualify","q":"A partner wants {unit}. How do you pitch and scope it?",
     "opts":["Pitch deck + scope doc from templates.","Custom pitch each time from scratch.","Verbal pitch — details settled later."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Custom pitches slow deals and introduce scope ambiguity.","missing":"Verbal-only deals create payment and delivery disputes."},
     "fix":"Pitch kit + scope templates"},
    {"name":"Produce","icon":"build","q":"Production on {unit} is underway. How is it managed?",
     "opts":["Production tracker with tasks, assets, and deadlines.","Shared drive and group chat.","Deadlines slip until someone panics."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Chat-based production loses versions and misses handoffs.","missing":"No production system means costly last-minute fire drills."},
     "fix":"Production management tool"},
    {"name":"Release","icon":"quote","q":"{unit} is ready to go live. How is release coordinated?",
     "opts":["Release checklist across platforms on one timeline.","Posted manually platform by platform.","Launch happens whenever it's 'good enough'."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Manual release creates inconsistent rollout and missed windows.","missing":"Unplanned launches waste the production investment."},
     "fix":"Release checklist + scheduler"},
    {"name":"Monetize","icon":"invoice","q":"After release, how do you track revenue from {unit}?",
     "opts":["Revenue dashboards tied to each release.","Spreadsheet updated monthly.","Not sure which releases actually made money."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Delayed revenue tracking hides what's working until too late.","missing":"No monetization view means you repeat unprofitable projects."},
     "fix":"Revenue attribution dashboard"},
    {"name":"Retain Fans","icon":"retain","q":"After {unit} drops, how do you keep the audience engaged?",
     "opts":["Post-release content plan with community touchpoints.","A few follow-up posts if there's time.","Silence until the next project."],
     "states":["solid","shaky","missing"],
     "diag":{"shaky":"Sparse follow-up lets heat dissipate before the next launch.","missing":"Long gaps between touchpoints reset audience growth."},
     "fix":"Community + content cadence"},
  ]
},
}

# Subtype-specific stage overrides (key stage customizations)
OVERRIDES = {
  ("service","IT & TECH"): {0: {"q":"A SaaS lead hits your site today. How did they find you and get logged?"}},
  ("service","LEGAL"): {1: {"q":"A potential client describes a case. How do you scope before quoting fees?"}},
  ("logistics","COLD CHAIN"): {2: {"q":"A temperature-sensitive {unit} is moving. Can you see breach risk in real time?",
    "opts":["Live temp sensors with alert thresholds at every handoff.","Driver checks temps at stops and texts updates.","We find out about a breach from the receiver."],
    "states":["solid","shaky","missing"],
    "diag":{"shaky":"Manual temp checks miss handoff gaps where product spoils.","missing":"No continuous monitoring makes claims and losses inevitable."},
    "fix":"Continuous temp monitoring"}},
  ("logistics","CUSTOMS"): {0: {"q":"An importer sends documents for {unit}. How is clearance intake handled?"}},
  ("manufacturing","FOOD & BEV"): {2: {"q":"On the line for {unit}, how is food safety monitored?",
    "opts":["HACCP logs and batch traceability in real time.","Checks done but records are partly paper.","Issues surface at customer complaint or audit."],
    "states":["solid","shaky","missing"],
    "diag":{"shaky":"Partial digital records slow recalls and increase scrap.","missing":"Weak food safety tracking is a recall waiting to happen."},
    "fix":"HACCP + traceability system"}},
  ("agriculture","CROP FARMING"): {2: {"q":"Mid-season on {unit}, how do you monitor crop health and inputs?"}},
  ("construction","FUEL/ENERGY"): {1: {"q":"A fuel/energy site job comes in. How do you estimate compliance and scope?"}},
  ("retail","E-COMMERCE"): {3: {"q":"An online order for {unit} comes in. How fast is it fulfilled and tracked?"}},
  ("finance","FINTECH"): {2: {"q":"A user completes KYC for {unit}. How fast is the account activated?"}},
  ("education","ED-TECH"): {2: {"q":"Learners are mid-module on {unit}. Can you see who is falling behind?"}},
  ("entertainment","GAMING"): {3: {"q":"Your {unit} build is ready. How is release coordinated across platforms?"}},
}

def fill(template: str, ctx: dict) -> str:
    out = template
    for k, v in ctx.items():
        out = out.replace("{" + k + "}", v)
    return out

def build_flow(category: str, subtype: str) -> dict:
    ctx = merge_ctx(category, subtype)
    base = FLOWS[category]
    stages = []
    for i, st in enumerate(base["stages"]):
        stage = dict(st)
        ov = OVERRIDES.get((category, subtype), {}).get(i, {})
        stage.update(ov)
        stage = {
            "name": stage["name"],
            "icon": "S3_ICON." + stage["icon"],
            "q": fill(stage["q"], ctx),
            "options": [{"text": fill(stage["opts"][j], ctx), "state": stage["states"][j]} for j in range(3)],
            "diag": {k: fill(v, ctx) for k, v in stage["diag"].items()},
            "fix": fill(stage["fix"], ctx),
        }
        stages.append(stage)
    return {"title": ctx["title"], "stages": stages}

# Build lookup table for all combos
lookup = {}
for cat, subtypes in S2.items():
    for st in subtypes:
        key = cat + "|" + slug(st)
        lookup[key] = build_flow(cat, st)

# Emit compact JS: store as precomputed flows
js_flows = "var S3_FLOW_LOOKUP = " + json.dumps(lookup, ensure_ascii=False, separators=(",", ":")) + ";\n"

resolver = r'''
function s3Slug(name) {
  return name.toLowerCase().replace(/\//g, '-').replace(/&/g, '').replace(/\s+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
}

function resolveS3Flow(categoryKey, subtypeName) {
  var key = categoryKey + '|' + s3Slug(subtypeName);
  var raw = S3_FLOW_LOOKUP[key];
  if (!raw) return S3_FLOW_DEFAULT;
  var stages = raw.stages.map(function(st) {
    return {
      name: st.name,
      icon: S3_ICON[st.icon],
      q: st.q,
      options: st.options.slice(),
      diag: { shaky: st.diag.shaky, missing: st.diag.missing },
      fix: st.fix
    };
  });
  return { title: raw.title, stages: stages };
}
'''

# Fix icon references in JSON - they were stored as strings "S3_ICON.lead"
for key, flow in lookup.items():
    for st in flow["stages"]:
        icon_key = st["icon"].replace("S3_ICON.", "")
        st["icon"] = icon_key

out_path = ROOT / "tools" / "s3-flow-data.js"
out_path.write_text(js_flows + resolver, encoding="utf-8")
print(f"Wrote {out_path} ({len(lookup)} flows)")
