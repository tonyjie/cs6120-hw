; ModuleID = 'simple.ll'
source_filename = "simple.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128"
target triple = "arm64-apple-macosx12.0.0"

@.str = private unnamed_addr constant [8 x i8] c"c = %d\0A\00", align 1

; Function Attrs: noinline nounwind ssp uwtable
define void @double_it(i32 %0) #0 {
  %2 = mul nsw i32 %0, 2
  ret void
}

; Function Attrs: noinline nounwind ssp uwtable
define i32 @main() #0 {
  br label %1

1:                                                ; preds = %13, %0
  %.01 = phi i32 [ 0, %0 ], [ %14, %13 ]
  %2 = icmp slt i32 %.01, 100
  br i1 %2, label %3, label %15

3:                                                ; preds = %1
  %4 = add nsw i32 2, 2
  call void @double_it(i32 %4)
  br label %5

5:                                                ; preds = %9, %3
  %.0 = phi i32 [ 0, %3 ], [ %10, %9 ]
  %6 = icmp slt i32 %.0, 20
  br i1 %6, label %7, label %11

7:                                                ; preds = %5
  %8 = mul nsw i32 2, 2
  call void @double_it(i32 %8)
  br label %9

9:                                                ; preds = %7
  %10 = add nsw i32 %.0, 1
  br label %5, !llvm.loop !9

11:                                               ; preds = %5
  %12 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([8 x i8], [8 x i8]* @.str, i64 0, i64 0), i32 %4)
  br label %13

13:                                               ; preds = %11
  %14 = add nsw i32 %.01, 1
  br label %1, !llvm.loop !11

15:                                               ; preds = %1
  ret i32 0
}

declare i32 @printf(i8*, ...) #1

attributes #0 = { noinline nounwind ssp uwtable "frame-pointer"="non-leaf" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+crc,+crypto,+dotprod,+fp-armv8,+fp16fml,+fullfp16,+lse,+neon,+ras,+rcpc,+rdm,+sha2,+v8.5a,+zcm,+zcz" }
attributes #1 = { "frame-pointer"="non-leaf" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+crc,+crypto,+dotprod,+fp-armv8,+fp16fml,+fullfp16,+lse,+neon,+ras,+rcpc,+rdm,+sha2,+v8.5a,+zcm,+zcz" }

!llvm.module.flags = !{!0, !1, !2, !3, !4, !5, !6, !7}
!llvm.ident = !{!8}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 1, !"branch-target-enforcement", i32 0}
!2 = !{i32 1, !"sign-return-address", i32 0}
!3 = !{i32 1, !"sign-return-address-all", i32 0}
!4 = !{i32 1, !"sign-return-address-with-bkey", i32 0}
!5 = !{i32 7, !"PIC Level", i32 2}
!6 = !{i32 7, !"uwtable", i32 1}
!7 = !{i32 7, !"frame-pointer", i32 1}
!8 = !{!"Homebrew clang version 13.0.1"}
!9 = distinct !{!9, !10}
!10 = !{!"llvm.loop.mustprogress"}
!11 = distinct !{!11, !10}
