from transformers import AutoProcessor, MarkupLMForQuestionAnswering
import torch

processor = AutoProcessor.from_pretrained("microsoft/markuplm-base-finetuned-websrc")
model = MarkupLMForQuestionAnswering.from_pretrained("microsoft/markuplm-base-finetuned-websrc")

html_string = """<body id="fsu-strata-three" class="home s3-bg-gt add-fixed"> 
<!-- Alerts -->
<!--<div class="s3-gd">
	<div class="container">
		<div class="row m-4">
			<div class="col-sm-12">

				<p class="lead text-center" style="margin: 0;"><span class="hidden-xs fa fa-exclamation-triangle"></span> <a href="http://alerts.fsu.edu/"></a> Hurricane Idalia: Check <a href="http://alerts.fsu.edu/">alerts.fsu.edu</a> for official FSU updates. <span class="hidden-xs fa fa-exclamation-triangle"></span></p>

			</div>
		</div>
	</div>
</div>-->

<!-- News -->
<div id="content" class="s3-w s3-scored">
    <div class="container s3-mt-8 s3-mb-6">
        <div class="row">
            <div class="col-xs-12">

</body>"""
question = "What salient content is in this page?"

encoding = processor(html_string, questions=question, return_tensors="pt")

with torch.no_grad():
    outputs = model(**encoding)

answer_start_index = outputs.start_logits.argmax()
answer_end_index = outputs.end_logits.argmax()

predict_answer_tokens = encoding.input_ids[0, answer_start_index : answer_end_index + 1]
print(processor.decode(predict_answer_tokens).strip())
