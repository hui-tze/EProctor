from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.home, name='home'),
    path('question/<str:pk>', views.question, name='question'),
    path('subject', views.subject, name='subject'),
    path('subject_question', views.subject_question, name='subject_question'),
    path('add_new_subject', views.add_new_subject, name='add_new_subject'),
    path('edit_subject/<str:pk>/', views.edit_subject, name='edit_subject'),
    path('delete_subject/<str:pk>/', views.delete_subject, name='delete_subject'),

    path('add_question', views.add_question, name='add_question'),
    path('edit_question/<str:pk>', views.edit_question, name='edit_question'),

    path('subject_exam', views.subject_exam, name='subject_exam'),
    path('examination', views.examination, name='examination'),
    path('add_examination', views.add_examination, name='add_examination'),
    path('edit_examination/<str:pk>', views.edit_examination, name='edit_examination'),
    path('delete_examination/<str:pk>', views.delete_examination, name='delete_examination'),
    path('get_max', views.get_max, name='get_max'),
    path('assign_student/<str:pk>/', views.assign_student, name='assign_student'),
    path('my_examination/<str:pk>/', views.my_examination, name='my_examination'),
    path('schedule_exam_list/<str:pk>/', views.schedule_exam_list, name='schedule_exam_list'),
    path('upcoming_exam_list/<str:pk>/', views.upcoming_exam_list, name='upcoming_exam_list'),
    path('exam_rules/<str:pk>', views.exam_rules, name='exam_rules'),
    path('start_exam/<str:pk>', views.start_exam, name='start_exam'),
    path('finish_exam/<str:pk>', views.finish_exam, name='finish_exam'),
    path('post_answer', views.post_answer, name='post_answer'),
    path('validate_code', views.validate_code, name='validate_code'),
    path('video_feed', views.video_feed, name='video_feed'),
    path('webcam_feed', views.webcam_feed, name='webcam_feed'),
    path('my_examination', views.my_examination, name='my_examination'),
    path('verification_before_exam/<str:id>', views.verification_before_exam, name='verification_before_exam'),
    path('validate_code', views.validate_code, name='validate_code'),
    path('verification_exam/<str:id>', views.verification_exam, name='verification_exam'),
    path('successful_verification/<str:id>', views.successful_verification, name='successful_verification'),
    path('video_feed/<str:pk>', views.video_feed, name='video_feed'),
    path('snapshot/<str:pk>', views.snapshot, name='snapshot'),
    path('view_result', views.view_result, name='view_result'),
    path('exam_result/<str:pk>', views.exam_result, name='exam_result'),
    path('student_result_list/<str:pk>', views.student_result_list, name='student_result_list'),
    path('view_snapshot/<str:sid>/<str:eid>', views.view_snapshot, name='view_snapshot'),
    path('view_result_paper/<str:sid>/<str:eid>', views.view_result_paper, name='view_result_paper'),
    path('my_result/<str:pk>', views.my_result, name='my_result'),
    path('student_answer/<str:pk>', views.student_answer, name='student_answer'),
    path('result_paper/<str:pk>', views.result_paper, name='result_paper'),
    path('student_result_paper/<str:pk>', views.student_result_paper, name='student_result_paper'),
    path('report', views.report, name='report'),
    path('report_view/<str:pk>', views.report_view, name='report_view'),

]