# 🗑️ BULK DELETE LINKS - Delete multiple links at once
@router.delete("/bulk-delete")
def bulk_delete_links(
    link_ids: List[int],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not link_ids:
        raise HTTPException(status_code=400, detail="No link IDs provided")
    
    # Find all links
    links = db.query(models.ShortLink).filter(
        models.ShortLink.id.in_(link_ids),
        models.ShortLink.user_id == current_user.id
    ).all()
    
    if not links:
        raise HTTPException(status_code=404, detail="No links found or you don't own these links")
    
    # Check if user owns all requested links
    found_ids = [link.id for link in links]
    not_found_ids = [link_id for link_id in link_ids if link_id not in found_ids]
    
    if not_found_ids:
        raise HTTPException(
            status_code=403, 
            detail=f"You don't own or these links don't exist: {not_found_ids}"
        )
    
    # Delete all links
    deleted_count = len(links)
    for link in links:
        db.delete(link)
    
    db.commit()
    
    return {
        "message": f"Successfully deleted {deleted_count} links",
        "deleted_count": deleted_count,
        "deleted_ids": found_ids
    }
