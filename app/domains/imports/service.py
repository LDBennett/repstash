import traceback
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.imports.models import ImportJob, ImportLog, JobStatus
from app.domains.exercises.scraper import scrape_social_url
from app.domains.exercises.ai_extractor import extract_exercises_from_content
from app.domains.exercises.models import Exercise, ExerciseMuscle

async def process_import_job(session: AsyncSession, job_id: int, source_url: str, user_id: int):
    # Fetch job
    job = await session.get(ImportJob, job_id)
    if not job:
        return
        
    job.status = JobStatus.PROCESSING
    await session.commit()
    
    import_log = ImportLog(job_id=job_id, source_url=source_url, status=JobStatus.PROCESSING)
    session.add(import_log)
    await session.commit()
    await session.refresh(import_log)
    log_id = import_log.id
    
    try:
        # Step 1: Scrape
        scrape_data = await scrape_social_url(source_url)
        import_log.raw_payload = scrape_data.caption
        
        # Step 2: AI Extract
        extraction = await extract_exercises_from_content(
            caption=scrape_data.caption, 
            video_bytes=scrape_data.video_bytes, 
            mime_type=scrape_data.mime_type
        )
        import_log.llm_prompt_used = "Gemini 2.5 Flash Structured Prompt"
        
        # Step 3: Save to DB
        for ex_data in extraction.exercises:
            exercise = Exercise(
                user_id=user_id,
                title=ex_data.title,
                description=ex_data.description,
                category=ex_data.category,
                equipment=ex_data.equipment,
                steps=ex_data.steps,
                default_sets=ex_data.default_sets,
                default_reps=ex_data.default_reps,
                default_weight_kg=ex_data.default_weight_kg,
                source_url=source_url
            )
            session.add(exercise)
            await session.flush() # get exercise.id
            
            for m in ex_data.muscles:
                em = ExerciseMuscle(
                    exercise_id=exercise.id,
                    muscle=m.muscle,
                    role=m.role
                )
                session.add(em)
                
        job.status = JobStatus.COMPLETED
        import_log.status = JobStatus.COMPLETED
        await session.commit()
        
    except Exception as e:
        await session.rollback()
        # Fetch them again to update status
        job = await session.get(ImportJob, job_id)
        if job:
            job.status = JobStatus.FAILED
            
        import_log = await session.get(ImportLog, log_id)
        if import_log:
            import_log.status = JobStatus.FAILED
            import_log.error_message = traceback.format_exc()
            
        await session.commit()
